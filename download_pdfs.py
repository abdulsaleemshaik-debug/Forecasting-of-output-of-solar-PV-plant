"""
Script to download PDFs for references in a Markdown file using Sci-Hub.
Relies on the cloned 'scihub.py' repository by zaytoun.
"""

import sys
import os
import re
import logging
from urllib.parse import urlparse

# Add scihub.py to path so we can import it
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scihub.py'))
from scihub.scihub import SciHub

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("scihub-scraper")


def parse_references(md_text: str):
    """Extract numbered references and DOIs from markdown text."""
    refs = []
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
        doi = None

        # Extract DOI
        doi_match = re.search(r"doi:\s*(10\.\S+)", raw, re.IGNORECASE)
        if doi_match:
            doi = doi_match.group(1).rstrip(".")

        refs.append({
            "number": num,
            "raw": raw,
            "doi": doi
        })

    return refs


def main():
    md_file = "Solar_PV_Forecasting_Journal_Paper.md"
    output_dir = "downloaded_references"
    
    if not os.path.exists(md_file):
        log.error(f"Markdown file {md_file} not found.")
        sys.exit(1)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()

    refs = parse_references(md_text)
    log.info(f"Found {len(refs)} references in {md_file}.")
    
    sh = SciHub()
    success_count = 0
    
    for ref in refs:
        if not ref["doi"]:
            log.warning(f"[{ref['number']}] No DOI found in reference text. Skipping.")
            continue
            
        doi = ref["doi"]
        log.info(f"[{ref['number']}] Fetching DOI: {doi}")
        
        try:
            # scihub.py takes an identifier (DOI) and path
            # the fetch method returns a dictionary with 'err' or pdf data
            result = sh.fetch(doi)
            
            if 'err' in result:
                log.error(f"[{ref['number']}] Sci-Hub error for {doi}: {result['err']}")
            elif 'pdf' in result:
                out_path = os.path.join(output_dir, f"Ref_{ref['number']:02d}_{doi.replace('/','_')}.pdf")
                with open(out_path, 'wb') as f:
                    f.write(result['pdf'])
                log.info(f"[{ref['number']}] ✅ Successfully downloaded to {out_path}")
                success_count += 1
            else:
                log.warning(f"[{ref['number']}] Unexpected response format for {doi}")
                
        except Exception as e:
            log.error(f"[{ref['number']}] Exception while fetching {doi}: {e}")
            
    log.info(f"Downloaded {success_count} / {len(refs)} PDFs successfully. Check the '{output_dir}' directory.")


if __name__ == "__main__":
    main()
