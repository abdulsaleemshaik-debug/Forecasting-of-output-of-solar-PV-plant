"""
Reference Verification & Citation Recommender Tool
===================================================
Automatically verifies academic references and recommends additional citations
using FREE legitimate APIs:

  1. CrossRef API     - DOI resolution, metadata verification (no auth)
  2. Semantic Scholar - Citation recommendations, related papers (no auth)
  3. OpenAlex API     - Open scholarly metadata, citation counts (no auth)

Usage:
    python verify_references.py [markdown_file]

If no file is specified, defaults to Solar_PV_Forecasting_Journal_Paper.md
"""

import re
import os
import sys
import json
import time
import logging
import argparse
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime

import requests
from rapidfuzz import fuzz

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ref-verify")

# ── API Configuration ──
CROSSREF_BASE = "https://api.crossref.org"
SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1"
OPENALEX_BASE = "https://api.openalex.org"

# Polite headers (CrossRef asks for a mailto for polite pool)
HEADERS = {
    "User-Agent": "ReferenceVerifier/1.0 (mailto:abdulsaleem@university.edu)",
}

# Rate limiting
RATE_LIMIT_DELAY = 1.0  # seconds between API calls


# ═══════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════


@dataclass
class Reference:
    """Parsed reference from the markdown paper."""
    number: int
    raw_text: str
    authors: str = ""
    title: str = ""
    journal: str = ""
    year: str = ""
    doi: str = ""
    needs_verification: bool = False


@dataclass
class VerificationResult:
    """Result of verifying a single reference."""
    ref_number: int
    ref_title: str
    ref_doi: str
    status: str = "UNVERIFIED"  # VERIFIED, PARTIAL, FAILED, NO_DOI, ERROR
    doi_resolves: Optional[bool] = None
    title_match_score: float = 0.0
    crossref_title: str = ""
    crossref_authors: str = ""
    crossref_journal: str = ""
    crossref_year: str = ""
    crossref_type: str = ""
    crossref_citation_count: int = 0
    openalex_citation_count: int = 0
    semantic_scholar_id: str = ""
    issues: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# REFERENCE PARSER
# ═══════════════════════════════════════════════════════════════


def parse_references(md_text: str) -> list[Reference]:
    """Extract numbered references from markdown text."""
    refs = []
    # Match [N] at start of line followed by reference text
    pattern = r"^\[(\d+)\]\s*(.+?)$"
    in_refs_section = False

    for line in md_text.split("\n"):
        if line.strip().startswith("## References"):
            in_refs_section = True
            continue
        if not in_refs_section:
            continue

        match = re.match(pattern, line.strip())
        if not match:
            continue

        num = int(match.group(1))
        raw = match.group(2).strip()

        ref = Reference(number=num, raw_text=raw)

        # Check if needs verification
        ref.needs_verification = "[NEEDS VERIFICATION]" in raw
        raw_clean = raw.replace("[NEEDS VERIFICATION]", "").strip()

        # Extract DOI
        doi_match = re.search(r"doi:\s*(10\.\S+)", raw_clean, re.IGNORECASE)
        if doi_match:
            ref.doi = doi_match.group(1).rstrip(".")

        # Extract title (between first pair of quotes)
        title_match = re.search(r'"([^"]+)"', raw_clean)
        if title_match:
            ref.title = title_match.group(1)

        # Extract year
        year_match = re.search(r",\s*((?:19|20)\d{2})\b", raw_clean)
        if year_match:
            ref.year = year_match.group(1)

        # Extract journal (between *...*)
        journal_match = re.search(r"\*([^*]+)\*", raw_clean)
        if journal_match:
            ref.journal = journal_match.group(1)

        # Extract authors (text before the first quote)
        author_match = re.match(r'^(.+?)[,"]', raw_clean)
        if author_match:
            ref.authors = author_match.group(1).strip().rstrip(",")

        refs.append(ref)

    log.info(f"Parsed {len(refs)} references ({sum(r.needs_verification for r in refs)} flagged for verification)")
    return refs


# ═══════════════════════════════════════════════════════════════
# API CLIENTS
# ═══════════════════════════════════════════════════════════════


class CrossRefClient:
    """CrossRef API client for DOI verification and metadata lookup."""

    @staticmethod
    def verify_doi(doi: str) -> Optional[dict]:
        """Resolve a DOI and return metadata from CrossRef."""
        if not doi:
            return None
        url = f"{CROSSREF_BASE}/works/{doi}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("message", {})
            elif resp.status_code == 404:
                log.warning(f"  DOI not found in CrossRef: {doi}")
                return None
            else:
                log.warning(f"  CrossRef returned {resp.status_code} for {doi}")
                return None
        except requests.RequestException as e:
            log.error(f"  CrossRef request failed: {e}")
            return None

    @staticmethod
    def search_by_title(title: str) -> Optional[dict]:
        """Search CrossRef by title to find matching works."""
        if not title:
            return None
        url = f"{CROSSREF_BASE}/works"
        params = {
            "query.title": title,
            "rows": 3,
            "select": "DOI,title,author,container-title,published-print,published-online,type,is-referenced-by-count",
        }
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                items = resp.json().get("message", {}).get("items", [])
                return items[0] if items else None
            return None
        except requests.RequestException as e:
            log.error(f"  CrossRef search failed: {e}")
            return None

    @staticmethod
    def extract_metadata(data: dict) -> dict:
        """Extract clean metadata from a CrossRef response."""
        authors = ""
        if "author" in data:
            author_list = []
            for a in data["author"][:6]:
                name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                if name:
                    author_list.append(name)
            authors = ", ".join(author_list)
            if len(data["author"]) > 6:
                authors += " et al."

        title = ""
        if "title" in data and data["title"]:
            title = data["title"][0] if isinstance(data["title"], list) else data["title"]

        journal = ""
        if "container-title" in data and data["container-title"]:
            journal = data["container-title"][0] if isinstance(data["container-title"], list) else data["container-title"]

        year = ""
        for date_field in ["published-print", "published-online", "created"]:
            if date_field in data and "date-parts" in data[date_field]:
                parts = data[date_field]["date-parts"]
                if parts and parts[0] and parts[0][0]:
                    year = str(parts[0][0])
                    break

        return {
            "title": title,
            "authors": authors,
            "journal": journal,
            "year": year,
            "type": data.get("type", ""),
            "citation_count": data.get("is-referenced-by-count", 0),
            "doi": data.get("DOI", ""),
        }


class SemanticScholarClient:
    """Semantic Scholar API client for citation recommendations."""

    @staticmethod
    def search_paper(title: str) -> Optional[dict]:
        """Search for a paper by title."""
        if not title:
            return None
        url = f"{SEMANTIC_SCHOLAR_BASE}/paper/search"
        params = {
            "query": title[:200],
            "limit": 1,
            "fields": "paperId,title,authors,year,citationCount,url,externalIds,citations.title,citations.year,citations.citationCount,references.title,references.year,references.citationCount",
        }
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                return data[0] if data else None
            return None
        except requests.RequestException as e:
            log.error(f"  Semantic Scholar search failed: {e}")
            return None

    @staticmethod
    def get_paper_by_doi(doi: str) -> Optional[dict]:
        """Get paper details by DOI."""
        if not doi:
            return None
        url = f"{SEMANTIC_SCHOLAR_BASE}/paper/DOI:{doi}"
        params = {
            "fields": "paperId,title,authors,year,citationCount,url,citations.title,citations.year,citations.citationCount,citations.externalIds,references.title,references.year,references.citationCount,references.externalIds",
        }
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            return None
        except requests.RequestException as e:
            log.error(f"  Semantic Scholar DOI lookup failed: {e}")
            return None

    @staticmethod
    def get_recommendations(paper_id: str, limit: int = 5) -> list:
        """Get recommended papers based on a given paper."""
        if not paper_id:
            return []
        url = f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{paper_id}"
        params = {
            "limit": limit,
            "fields": "title,authors,year,citationCount,externalIds,url",
        }
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("recommendedPapers", [])
            return []
        except requests.RequestException as e:
            log.error(f"  Semantic Scholar recommendations failed: {e}")
            return []


class OpenAlexClient:
    """OpenAlex API client for citation counts and open metadata."""

    @staticmethod
    def search_by_doi(doi: str) -> Optional[dict]:
        """Search OpenAlex by DOI."""
        if not doi:
            return None
        url = f"{OPENALEX_BASE}/works/doi:{doi}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            return None
        except requests.RequestException as e:
            log.error(f"  OpenAlex DOI lookup failed: {e}")
            return None

    @staticmethod
    def search_by_title(title: str) -> Optional[dict]:
        """Search OpenAlex by title."""
        if not title:
            return None
        url = f"{OPENALEX_BASE}/works"
        params = {
            "search": title[:200],
            "per_page": 1,
        }
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                return results[0] if results else None
            return None
        except requests.RequestException as e:
            log.error(f"  OpenAlex search failed: {e}")
            return None


# ═══════════════════════════════════════════════════════════════
# VERIFICATION ENGINE
# ═══════════════════════════════════════════════════════════════


class ReferenceVerifier:
    """Main verification engine that orchestrates all API calls."""

    def __init__(self):
        self.crossref = CrossRefClient()
        self.semantic = SemanticScholarClient()
        self.openalex = OpenAlexClient()

    def verify_reference(self, ref: Reference) -> VerificationResult:
        """Verify a single reference against all available APIs."""
        result = VerificationResult(
            ref_number=ref.number,
            ref_title=ref.title,
            ref_doi=ref.doi,
        )

        log.info(f"[{ref.number}] Verifying: {ref.title[:70]}...")

        # ── Step 1: CrossRef DOI verification ──
        crossref_data = None
        if ref.doi:
            crossref_data = self.crossref.verify_doi(ref.doi)
            if crossref_data:
                result.doi_resolves = True
                meta = self.crossref.extract_metadata(crossref_data)
                result.crossref_title = meta["title"]
                result.crossref_authors = meta["authors"]
                result.crossref_journal = meta["journal"]
                result.crossref_year = meta["year"]
                result.crossref_type = meta["type"]
                result.crossref_citation_count = meta["citation_count"]

                # Title match scoring
                if ref.title and meta["title"]:
                    result.title_match_score = fuzz.token_sort_ratio(
                        ref.title.lower(), meta["title"].lower()
                    )
            else:
                result.doi_resolves = False
                result.issues.append(f"DOI {ref.doi} does NOT resolve in CrossRef")
        else:
            result.doi_resolves = None
            result.issues.append("No DOI provided")

        time.sleep(RATE_LIMIT_DELAY)

        # ── Step 2: If DOI failed, try title search in CrossRef ──
        if not crossref_data and ref.title:
            log.info(f"  Searching CrossRef by title...")
            crossref_data = self.crossref.search_by_title(ref.title)
            if crossref_data:
                meta = self.crossref.extract_metadata(crossref_data)
                title_score = fuzz.token_sort_ratio(
                    ref.title.lower(), meta["title"].lower()
                ) if ref.title and meta["title"] else 0

                if title_score > 70:
                    result.crossref_title = meta["title"]
                    result.crossref_authors = meta["authors"]
                    result.crossref_journal = meta["journal"]
                    result.crossref_year = meta["year"]
                    result.crossref_type = meta["type"]
                    result.crossref_citation_count = meta["citation_count"]
                    result.title_match_score = title_score

                    if not ref.doi and meta["doi"]:
                        result.issues.append(f"Suggested DOI: {meta['doi']}")
                else:
                    log.info(f"  Title match too low ({title_score}%), skipping")

            time.sleep(RATE_LIMIT_DELAY)

        # ── Step 3: OpenAlex citation count ──
        openalex_data = None
        if ref.doi:
            openalex_data = self.openalex.search_by_doi(ref.doi)
        if not openalex_data and ref.title:
            openalex_data = self.openalex.search_by_title(ref.title)
        if openalex_data:
            result.openalex_citation_count = openalex_data.get("cited_by_count", 0)

        time.sleep(RATE_LIMIT_DELAY)

        # ── Step 4: Cross-validate metadata ──
        self._cross_validate(ref, result)

        # ── Step 5: Determine overall status ──
        result.status = self._determine_status(ref, result)

        return result

    def _cross_validate(self, ref: Reference, result: VerificationResult):
        """Cross-validate paper metadata against reference text."""
        # Year mismatch check
        if ref.year and result.crossref_year:
            if ref.year != result.crossref_year:
                result.issues.append(
                    f"Year mismatch: paper says {ref.year}, CrossRef says {result.crossref_year}"
                )

        # Journal name check
        if ref.journal and result.crossref_journal:
            journal_score = fuzz.token_sort_ratio(
                ref.journal.lower(), result.crossref_journal.lower()
            )
            if journal_score < 60:
                result.issues.append(
                    f"Journal mismatch: paper says '{ref.journal}', CrossRef says '{result.crossref_journal}'"
                )

        # Title similarity check
        if result.title_match_score > 0 and result.title_match_score < 80:
            result.issues.append(
                f"Title partially matches ({result.title_match_score:.0f}%): '{result.crossref_title[:80]}'"
            )

    def _determine_status(self, ref: Reference, result: VerificationResult) -> str:
        """Determine overall verification status."""
        if result.doi_resolves and result.title_match_score >= 85:
            if not any("mismatch" in i.lower() for i in result.issues):
                return "VERIFIED"
            return "PARTIAL"
        elif result.doi_resolves and result.title_match_score >= 60:
            return "PARTIAL"
        elif result.doi_resolves is False:
            return "FAILED"
        elif not ref.doi:
            if result.crossref_title and result.title_match_score >= 70:
                return "PARTIAL"
            return "NO_DOI"
        else:
            return "UNVERIFIED"

    def get_citation_recommendations(self, refs: list[Reference], top_n: int = 10) -> list:
        """
        Get citation recommendations based on the paper's existing references.
        Uses Semantic Scholar to find highly-cited papers related to the topic.
        """
        log.info("\n" + "=" * 60)
        log.info("GENERATING CITATION RECOMMENDATIONS...")
        log.info("=" * 60)

        # Use a few key references (those with DOIs) to seed recommendations
        all_recommendations = []
        seen_titles = set()
        existing_titles = {r.title.lower() for r in refs if r.title}

        # Pick up to 5 well-known references for recommendations
        seed_refs = [r for r in refs if r.doi][:5]

        for ref in seed_refs:
            log.info(f"  Getting recommendations from ref [{ref.number}]...")

            # Get paper ID from Semantic Scholar
            paper_data = self.semantic.get_paper_by_doi(ref.doi)
            if not paper_data:
                time.sleep(RATE_LIMIT_DELAY)
                continue

            paper_id = paper_data.get("paperId", "")

            # Collect citing papers (papers that cite this reference)
            citations = paper_data.get("citations", []) or []
            for cite in citations[:10]:
                if not cite or not cite.get("title"):
                    continue
                title_lower = cite["title"].lower()
                if title_lower not in seen_titles and title_lower not in existing_titles:
                    seen_titles.add(title_lower)
                    cite["_source"] = f"cites ref [{ref.number}]"
                    all_recommendations.append(cite)

            # Collect references of (papers referenced by this reference)
            references = paper_data.get("references", []) or []
            for refpaper in references[:10]:
                if not refpaper or not refpaper.get("title"):
                    continue
                title_lower = refpaper["title"].lower()
                if title_lower not in seen_titles and title_lower not in existing_titles:
                    seen_titles.add(title_lower)
                    refpaper["_source"] = f"referenced by ref [{ref.number}]"
                    all_recommendations.append(refpaper)

            # Get algorithmic recommendations
            if paper_id:
                recs = self.semantic.get_recommendations(paper_id, limit=5)
                for rec in recs:
                    if not rec or not rec.get("title"):
                        continue
                    title_lower = rec["title"].lower()
                    if title_lower not in seen_titles and title_lower not in existing_titles:
                        seen_titles.add(title_lower)
                        rec["_source"] = f"recommended from ref [{ref.number}]"
                        all_recommendations.append(rec)

            time.sleep(RATE_LIMIT_DELAY)

        # Sort by citation count and return top N
        all_recommendations.sort(
            key=lambda x: x.get("citationCount", 0) or 0,
            reverse=True
        )

        return all_recommendations[:top_n]


# ═══════════════════════════════════════════════════════════════
# REPORT GENERATOR
# ═══════════════════════════════════════════════════════════════


def generate_report(
    results: list[VerificationResult],
    recommendations: list,
    output_path: str = "reference_verification_report.md",
):
    """Generate a comprehensive markdown verification report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []

    lines.append("# Reference Verification & Citation Recommendation Report")
    lines.append(f"\n**Generated:** {now}")
    lines.append(f"**Total References:** {len(results)}")

    # Summary statistics
    verified = sum(1 for r in results if r.status == "VERIFIED")
    partial = sum(1 for r in results if r.status == "PARTIAL")
    failed = sum(1 for r in results if r.status == "FAILED")
    no_doi = sum(1 for r in results if r.status == "NO_DOI")
    unverified = sum(1 for r in results if r.status in ("UNVERIFIED", "ERROR"))

    lines.append("\n## Summary")
    lines.append("")
    lines.append(f"| Status | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| ✅ VERIFIED | {verified} |")
    lines.append(f"| ⚠️ PARTIAL | {partial} |")
    lines.append(f"| ❌ FAILED | {failed} |")
    lines.append(f"| 🔍 NO DOI | {no_doi} |")
    lines.append(f"| ❓ UNVERIFIED | {unverified} |")

    # APIs used
    lines.append("\n## APIs Used")
    lines.append("")
    lines.append("| API | URL | Purpose |")
    lines.append("|-----|-----|---------|")
    lines.append("| CrossRef | `https://api.crossref.org` | DOI verification, metadata |")
    lines.append("| Semantic Scholar | `https://api.semanticscholar.org` | Citation recommendations |")
    lines.append("| OpenAlex | `https://api.openalex.org` | Citation counts, open metadata |")

    # Detailed results
    lines.append("\n---\n")
    lines.append("## Detailed Verification Results")

    for r in results:
        icon = {"VERIFIED": "✅", "PARTIAL": "⚠️", "FAILED": "❌", "NO_DOI": "🔍", "UNVERIFIED": "❓", "ERROR": "❓"}
        status_icon = icon.get(r.status, "❓")

        lines.append(f"\n### [{r.ref_number}] {status_icon} {r.status}")
        lines.append(f"**Title:** {r.ref_title}")
        lines.append(f"**DOI:** {r.ref_doi or 'None'}")

        if r.doi_resolves is not None:
            lines.append(f"**DOI Resolves:** {'Yes ✅' if r.doi_resolves else 'No ❌'}")

        if r.title_match_score > 0:
            lines.append(f"**Title Match Score:** {r.title_match_score:.0f}%")

        if r.crossref_title:
            lines.append(f"\n**CrossRef Data:**")
            lines.append(f"- Title: {r.crossref_title}")
            lines.append(f"- Authors: {r.crossref_authors}")
            lines.append(f"- Journal: {r.crossref_journal}")
            lines.append(f"- Year: {r.crossref_year}")
            lines.append(f"- Type: {r.crossref_type}")
            lines.append(f"- CrossRef Citations: {r.crossref_citation_count}")

        if r.openalex_citation_count > 0:
            lines.append(f"- OpenAlex Citations: {r.openalex_citation_count}")

        if r.issues:
            lines.append(f"\n**Issues Found:**")
            for issue in r.issues:
                lines.append(f"- ⚡ {issue}")

    # Citation Recommendations
    if recommendations:
        lines.append("\n---\n")
        lines.append("## 📚 Recommended Additional Citations")
        lines.append("")
        lines.append("These papers are highly cited and related to your references. Consider adding them:")
        lines.append("")
        lines.append("| # | Title | Year | Citations | Source | DOI |")
        lines.append("|---|-------|------|-----------|--------|-----|")

        for i, rec in enumerate(recommendations, 1):
            title = rec.get("title", "Unknown")[:80]
            year = rec.get("year", "—") or "—"
            cites = rec.get("citationCount", 0) or 0
            source = rec.get("_source", "—")

            # Try to get DOI
            ext_ids = rec.get("externalIds", {}) or {}
            doi = ext_ids.get("DOI", "")
            doi_str = f"`{doi}`" if doi else "—"

            lines.append(f"| {i} | {title} | {year} | {cites} | {source} | {doi_str} |")

    # Footer
    lines.append("\n---\n")
    lines.append("## How to Use This Report")
    lines.append("")
    lines.append("1. **VERIFIED** references need no action")
    lines.append("2. **PARTIAL** references have minor discrepancies — review the issues listed")
    lines.append("3. **FAILED** references have DOIs that don't resolve — check for typos")
    lines.append("4. **NO DOI** references could not be independently verified — add a DOI if possible")
    lines.append("5. Review **Recommended Additional Citations** for relevant papers to strengthen your bibliography")
    lines.append("")
    lines.append("*Report generated by Reference Verification Tool using CrossRef, Semantic Scholar, and OpenAlex APIs.*")

    report = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    log.info(f"\nReport saved to: {output_path}")
    return report


def generate_json_report(results: list[VerificationResult], output_path: str = "reference_verification.json"):
    """Save structured verification data as JSON."""
    data = {
        "generated": datetime.now().isoformat(),
        "total_references": len(results),
        "summary": {
            "verified": sum(1 for r in results if r.status == "VERIFIED"),
            "partial": sum(1 for r in results if r.status == "PARTIAL"),
            "failed": sum(1 for r in results if r.status == "FAILED"),
            "no_doi": sum(1 for r in results if r.status == "NO_DOI"),
        },
        "results": [asdict(r) for r in results],
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log.info(f"JSON data saved to: {output_path}")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="Verify academic references and recommend citations using CrossRef, Semantic Scholar, and OpenAlex APIs."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="Solar_PV_Forecasting_Journal_Paper.md",
        help="Markdown file containing references to verify",
    )
    parser.add_argument(
        "--skip-recommendations",
        action="store_true",
        help="Skip citation recommendation generation (faster)",
    )
    parser.add_argument(
        "--output",
        default="reference_verification_report.md",
        help="Output report file path",
    )
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Read input file
    if not os.path.exists(args.input_file):
        log.error(f"File not found: {args.input_file}")
        sys.exit(1)

    with open(args.input_file, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Parse references
    refs = parse_references(md_text)
    if not refs:
        log.error("No references found in the file.")
        sys.exit(1)

    # Verify each reference
    verifier = ReferenceVerifier()
    results = []

    print("\n" + "=" * 60)
    print("REFERENCE VERIFICATION")
    print("=" * 60)

    for ref in refs:
        result = verifier.verify_reference(ref)
        results.append(result)

        icon = {"VERIFIED": "✅", "PARTIAL": "⚠️", "FAILED": "❌", "NO_DOI": "🔍"}.get(result.status, "❓")
        print(f"  [{ref.number:2d}] {icon} {result.status:10s} | {ref.title[:60]}")
        if result.issues:
            for issue in result.issues:
                print(f"       ⚡ {issue}")

    # Citation recommendations
    recommendations = []
    if not args.skip_recommendations:
        recommendations = verifier.get_citation_recommendations(refs, top_n=15)

    # Generate reports
    print("\n" + "=" * 60)
    print("GENERATING REPORTS")
    print("=" * 60)

    generate_report(results, recommendations, args.output)
    generate_json_report(results)

    # Print summary
    verified = sum(1 for r in results if r.status == "VERIFIED")
    partial = sum(1 for r in results if r.status == "PARTIAL")
    failed = sum(1 for r in results if r.status == "FAILED")

    print(f"\n{'=' * 60}")
    print(f"SUMMARY: {verified} verified, {partial} partial, {failed} failed")
    print(f"Recommendations: {len(recommendations)} papers suggested")
    print(f"Reports: {args.output}, reference_verification.json")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
