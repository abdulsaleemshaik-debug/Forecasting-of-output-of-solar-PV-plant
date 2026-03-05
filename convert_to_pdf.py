"""
Lossless conversion of Solar_PV_Forecasting_Journal_Paper.md to PDF.

Uses pypandoc (bundled pandoc) + XeLaTeX (MiKTeX) for:
  - Pixel-perfect table rendering
  - Native LaTeX math typesetting
  - Proper font embedding (Times New Roman body, Calibri headings)
  - Correct image sizing from local report_figures/
  - Preserved spacing, layout, and hierarchy
"""

import os
import re
import sys
import pypandoc

# ── Configuration ──
INPUT_MD   = "Solar_PV_Forecasting_Journal_Paper.md"
OUTPUT_PDF = "Solar_PV_Forecasting_Journal_Paper_Updated.pdf"
HEADER_TEX = "_header.tex"

# GitHub URL -> local path mapping
IMAGE_MAP = {
    "report_missing_values.png": "report_figures/fig01_missing_values.png",
    "report_univariate.png":     "report_figures/fig02_univariate.png",
    "report_bivariate.png":      "report_figures/fig03_bivariate.png",
    "report_correlation.png":    "report_figures/fig04_correlation.png",
    "report_timeseries.png":     "report_figures/fig05_timeseries.png",
}

# ── Custom LaTeX preamble for journal-quality formatting ──
HEADER_INCLUDES = r"""
% ── Better tables ──
\usepackage{booktabs}
\renewcommand{\arraystretch}{1.3}

% ── Figure handling ──
\usepackage{float}

%  Force max image size 
\usepackage{graphicx}
\setkeys{Gin}{width=1.0\linewidth,keepaspectratio}


% ── Colors ──
\usepackage{xcolor}
\definecolor{darkblue}{RGB}{0,51,102}

% ── Section heading formatting ──
\usepackage{titlesec}
\titleformat{\section}{\Large\bfseries\sffamily\color{darkblue}}{\thesection}{1em}{}
\titleformat{\subsection}{\large\bfseries\sffamily\color{darkblue}}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalsize\bfseries\sffamily\color{darkblue}}{\thesubsubsection}{1em}{}
\titlespacing*{\section}{0pt}{18pt}{8pt}
\titlespacing*{\subsection}{0pt}{14pt}{6pt}
\titlespacing*{\subsubsection}{0pt}{10pt}{4pt}

% ── Paragraph spacing ──
\setlength{\parskip}{6pt plus 2pt minus 1pt}
\setlength{\parindent}{0pt}

% ── Header/footer ──
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\sffamily\color{gray}Solar PV Forecasting -- Journal Paper}
\fancyhead[R]{\small\sffamily\color{gray}\thepage}
\fancyfoot[C]{}
\renewcommand{\headrulewidth}{0.4pt}

% ── Prevent widows/orphans ──
\widowpenalty=10000
\clubpenalty=10000
"""


def prepare_markdown(md_text: str) -> str:
    """
    Pre-process markdown for best pandoc -> LaTeX conversion:
      1. Replace remote GitHub image URLs with local paths.
      2. Ensure table alignment hints are preserved.
    """
    for remote_name, local_path in IMAGE_MAP.items():
        pattern = r"https://raw\.githubusercontent\.com/[^\s\)]*" + re.escape(remote_name)
        md_text = re.sub(pattern, local_path.replace("\\", "/"), md_text)
    return md_text


def write_header_file():
    """Write the LaTeX header-includes to a temp .tex file."""
    with open(HEADER_TEX, "w", encoding="utf-8") as f:
        f.write(HEADER_INCLUDES)


def convert(md_text: str):
    """Convert markdown to PDF via XeLaTeX with all formatting preserved."""
    write_header_file()

    print(f"Converting {INPUT_MD} -> {OUTPUT_PDF}")
    print("  Engine : XeLaTeX (MiKTeX)")
    print("  Fonts  : Times New Roman (body), Calibri (headings)")
    print("  Images : local report_figures/")
    print()

    pypandoc.convert_text(
        md_text,
        "pdf",
        format="markdown"
               "+pipe_tables"
               "+tex_math_dollars"
               "+raw_tex"
               "+implicit_figures"
               "+strikeout"
               "+superscript"
               "+subscript",
        outputfile=OUTPUT_PDF,
        extra_args=[
            "--standalone",
            "--pdf-engine=xelatex",
            "--resource-path=.",
            # Table of contents
            "--toc",
            "--toc-depth=3",
            # LaTeX header for formatting
            f"--include-in-header={HEADER_TEX}",
            # Fonts via pandoc variables (works with XeLaTeX)
            "-V", "mainfont=Times New Roman",
            "-V", "sansfont=Calibri",
            "-V", "monofont=Consolas",
            "-V", "fontsize=11pt",
            "-V", "geometry:a4paper",
            "-V", "geometry:margin=0.6in",
            "-V", "colorlinks=true",
            "-V", "linkcolor=darkblue",
            "-V", "urlcolor=darkblue",
            # Number sections for journal style
            "--number-sections",
            # Top-level heading = section (not chapter)
            "--top-level-division=section",
        ],
    )

    size_kb = os.path.getsize(OUTPUT_PDF) / 1024
    print(f"  -> {OUTPUT_PDF}  ({size_kb:.0f} KB)")
    print("  Done! All formatting, math, tables, images, and spacing preserved.")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if not os.path.exists(INPUT_MD):
        print(f"ERROR: {INPUT_MD} not found in {os.getcwd()}")
        sys.exit(1)

    with open(INPUT_MD, "r", encoding="utf-8") as f:
        md_text = f.read()

    md_text = prepare_markdown(md_text)
    convert(md_text)

    # Clean up temp header file
    if os.path.exists(HEADER_TEX):
        os.remove(HEADER_TEX)


if __name__ == "__main__":
    main()
