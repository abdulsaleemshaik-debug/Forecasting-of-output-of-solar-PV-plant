"""
Convert Solar_PV_Forecasting_Journal_Paper.md to Word (DOCX) and PDF formats.
Uses pypandoc (bundled pandoc) for conversion.
Replaces remote GitHub image URLs with local report_figures/ paths.
"""

import os
import re
import pypandoc

# ----- Configuration -----
INPUT_MD = "Solar_PV_Forecasting_Journal_Paper.md"
OUTPUT_DOCX = "Solar_PV_Forecasting_Journal_Paper.docx"
OUTPUT_PDF = "Solar_PV_Forecasting_Journal_Paper.pdf"

# Mapping: GitHub filename fragment -> local figure path
IMAGE_MAP = {
    "report_missing_values.png": "report_figures/fig01_missing_values.png",
    "report_univariate.png": "report_figures/fig02_univariate.png",
    "report_bivariate.png": "report_figures/fig03_bivariate.png",
    "report_correlation.png": "report_figures/fig04_correlation.png",
    "report_timeseries.png": "report_figures/fig05_timeseries.png",
}

def prepare_markdown(md_text: str) -> str:
    """Replace remote GitHub image URLs with local paths."""
    for remote_name, local_path in IMAGE_MAP.items():
        # Match the full GitHub raw URL containing this filename
        pattern = r"https://raw\.githubusercontent\.com/[^\s\)]*" + re.escape(remote_name)
        md_text = re.sub(pattern, local_path, md_text)
    return md_text


def convert_to_docx(md_text: str):
    """Convert markdown text to DOCX using pandoc."""
    print(f"Converting to {OUTPUT_DOCX} ...")
    pypandoc.convert_text(
        md_text,
        "docx",
        format="markdown+pipe_tables+tex_math_dollars",
        outputfile=OUTPUT_DOCX,
        extra_args=[
            "--standalone",
            "--toc",                       # Table of contents
            "--toc-depth=3",
            "--resource-path=.",
        ],
    )
    size_kb = os.path.getsize(OUTPUT_DOCX) / 1024
    print(f"  -> {OUTPUT_DOCX} created ({size_kb:.0f} KB)")


def convert_to_pdf(md_text: str):
    """
    Convert markdown text to PDF.
    Tries LaTeX engine first; falls back to HTML->PDF via wkhtmltopdf or
    built-in pdf engine.
    """
    print(f"Converting to {OUTPUT_PDF} ...")

    # Try 1: LaTeX-based PDF (best quality for math)
    try:
        pypandoc.convert_text(
            md_text,
            "pdf",
            format="markdown+pipe_tables+tex_math_dollars",
            outputfile=OUTPUT_PDF,
            extra_args=[
                "--standalone",
                "--toc",
                "--toc-depth=3",
                "--resource-path=.",
                "--pdf-engine=xelatex",
                "-V", "geometry:margin=1in",
                "-V", "fontsize=11pt",
                "-V", "mainfont=Calibri",
            ],
        )
        size_kb = os.path.getsize(OUTPUT_PDF) / 1024
        print(f"  -> {OUTPUT_PDF} created via LaTeX ({size_kb:.0f} KB)")
        return
    except Exception as e:
        print(f"  LaTeX engine not available ({e}), trying HTML route...")

    # Try 2: HTML intermediate -> PDF
    try:
        pypandoc.convert_text(
            md_text,
            "pdf",
            format="markdown+pipe_tables+tex_math_dollars",
            outputfile=OUTPUT_PDF,
            extra_args=[
                "--standalone",
                "--toc",
                "--toc-depth=3",
                "--resource-path=.",
                "--pdf-engine=wkhtmltopdf",
                "--mathjax",
            ],
        )
        size_kb = os.path.getsize(OUTPUT_PDF) / 1024
        print(f"  -> {OUTPUT_PDF} created via wkhtmltopdf ({size_kb:.0f} KB)")
        return
    except Exception as e:
        print(f"  wkhtmltopdf not available ({e}), trying html5 route...")

    # Try 3: Generate HTML and convert with weasyprint / pdflatex fallback
    try:
        html_intermediate = "Solar_PV_Forecasting_Journal_Paper.html"
        pypandoc.convert_text(
            md_text,
            "html5",
            format="markdown+pipe_tables+tex_math_dollars",
            outputfile=html_intermediate,
            extra_args=[
                "--standalone",
                "--toc",
                "--toc-depth=3",
                "--resource-path=.",
                "--mathjax",
                "--metadata", "title=Solar PV Forecasting Journal Paper",
            ],
        )
        size_kb = os.path.getsize(html_intermediate) / 1024
        print(f"  -> {html_intermediate} created ({size_kb:.0f} KB)")
        print(f"  NOTE: PDF generation requires a LaTeX distribution (MiKTeX/TeX Live)")
        print(f"        or wkhtmltopdf. Install one of these and re-run, or open the")
        print(f"        HTML file in a browser and use Print -> Save as PDF.")
    except Exception as e:
        print(f"  HTML generation also failed: {e}")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with open(INPUT_MD, "r", encoding="utf-8") as f:
        md_text = f.read()

    md_text = prepare_markdown(md_text)

    convert_to_docx(md_text)
    convert_to_pdf(md_text)

    print("\nDone!")


if __name__ == "__main__":
    main()
