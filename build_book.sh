#!/usr/bin/env bash

set -euo pipefail

# Build collected books (Workshops, Talks, All) from ordered links in index.md files
# Outputs:
# - Per-source processed Markdown mirrors under ./ebook/src/{workshops,talks}/...
# - Per-source LaTeX mirrors under   ./ebook/tex/{workshops,talks}/...
# - Master LaTeX that uses \include to stitch per-source .tex files
# - PDFs for workshops, talks, and full book

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
EBOOK_DIR="$REPO_ROOT/ebook"
WORKSHOPS_DIR="$REPO_ROOT/docs/workshops"
TALKS_DIR="$REPO_ROOT/docs/talks"

mkdir -p "$EBOOK_DIR"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing dependency: $1" >&2
    return 1
  fi
}

check_deps() {
  local missing=0
  need_cmd pandoc || missing=1
  if ! command -v tectonic >/dev/null 2>&1; then
    echo "Note: 'tectonic' not found; pandoc will try a different LaTeX engine which may fail without a TeX distribution." >&2
    echo "Install with: brew install tectonic" >&2
  fi
  if command -v mmdc >/dev/null 2>&1; then
    :
  else
    echo "Note: 'mmdc' (mermaid-cli) not found; Mermaid diagrams in code blocks will not render as images." >&2
    echo "Install with: npm install -g @mermaid-js/mermaid-cli" >&2
  fi
  if [[ "$missing" -eq 1 ]]; then
    echo "Install pandoc with: brew install pandoc" >&2
    exit 1
  fi
}

parse_and_prepare() {
  # $1: index.md path
  # $2: base dir
  # $3: out dir for processed markdown mirror (under ebook/src/...)
  # $4: file list output (for later conversion)
  local index_path="$1"
  local base_dir="$2"
  local out_src_dir="$3"
  local out_list_file="$4"

  python3 - "$index_path" "$base_dir" "$out_src_dir" "$out_list_file" << 'PY'
import re
import sys
from pathlib import Path

index_path = Path(sys.argv[1])
base_dir = Path(sys.argv[2])
out_src_dir = Path(sys.argv[3])
out_list_file = Path(sys.argv[4])

content = index_path.read_text(encoding="utf-8")

# Extract .md links in order of appearance
links = re.findall(r"\]\(([^)]+\.md)\)", content)

# Normalize and filter to existing files within base_dir
ordered_files = []
seen = set()
for href in links:
    # Ignore external or absolute links
    if href.startswith("http://") or href.startswith("https://"):
        continue
    candidate = (index_path.parent / href).resolve()
    try:
        candidate.relative_to(base_dir)
    except Exception:
        continue
    if candidate.exists() and candidate.suffix == ".md":
        if candidate not in seen:
            seen.add(candidate)
            ordered_files.append(candidate)

def strip_front_matter(text: str) -> str:
    # Remove leading YAML front matter if present
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end+5:]
    return text

def convert_admonitions(md: str) -> str:
    lines = md.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^!!!\s+(\w+)(?:\s+"([^"]+)")?\s*$', line)
        if m:
            kind = m.group(1).upper()
            title = m.group(2) or ''
            out.append(f"> **{kind}**: {title}".rstrip())
            i += 1
            # capture indented block
            while i < len(lines):
                nxt = lines[i]
                if nxt.startswith('    '):
                    out.append('> ' + nxt[4:])
                    i += 1
                elif nxt.strip() == '':
                    out.append('>')
                    i += 1
                else:
                    break
            continue
        out.append(line)
        i += 1
    return "\n".join(out)

# Prepare output mirror
out_src_dir.mkdir(parents=True, exist_ok=True)
for src in ordered_files:
    rel = src.relative_to(base_dir)
    dest = out_src_dir / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="utf-8")
    text = strip_front_matter(text)
    # Character replacements for LaTeX compatibility
    replacements = {
        "✅": "[OK]",
        "❌": "[X]", 
        "✔️": "[OK]",
        "✖️": "[X]",
        "🚀": "(rocket)",
        "💡": "(idea)",
        "📝": "(note)",
        "🔥": "(fire)",
        "→": "->",
        "←": "<-",
        "↑": "^",
        "↓": "v",
        """: '"',
        """: '"',
        "'": "'",
        "'": "'",
        "–": "--",
        "—": "---",
        "…": "...",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Convert mkdocs admonitions to blockquotes
    text = convert_admonitions(text)
    # Avoid broken intra-file links to .md in PDF (keep text only)
    text = re.sub(r"\]\(([^)]+\.md)\)", "]", text)
    dest.write_text(text, encoding="utf-8")

out_list_file.parent.mkdir(parents=True, exist_ok=True)
out_list_file.write_text("\n".join(str(p) for p in ordered_files), encoding="utf-8")
print(f"Prepared {len(ordered_files)} files into {out_src_dir}")
PY
}

convert_src_to_tex() {
  # $1: src base dir (ebook/src/workshops or talks)
  # $2: tex base dir (ebook/tex/workshops or talks)
  # $3: list file of original md paths, used to derive mirror names
  # $4: section type (workshops or talks)
  local src_base="$1"
  local tex_base="$2"
  local list_file="$3"
  local section_type="$4"
  local lua_filter="$REPO_ROOT/scripts/filters/mermaid.lua"

  mkdir -p "$tex_base"

  local chapter_num=0
  if [[ "$section_type" == "workshops" ]]; then
    chapter_num=0  # Start workshops from Chapter 0
  else
    chapter_num=1  # Start talks from Chapter 1 (will be adjusted)
  fi

  while IFS= read -r orig; do
    [[ -z "$orig" ]] && continue
    # Mirror relative path under src_base
    local rel
    rel="${orig#$WORKSHOPS_DIR/}"
    if [[ "$orig" != "$WORKSHOPS_DIR/"* ]]; then
      rel="${orig#$TALKS_DIR/}"
    fi
    local src_md="$src_base/$rel"
    local out_tex="$tex_base/${rel%.md}.tex"
    mkdir -p "$(dirname "$out_tex")"
    
    # Add chapter command at the beginning of each file and fix numbering
    local temp_md=$(mktemp)
    local filename=$(basename "$rel" .md)
    
    # Extract title from markdown file
    local title=$(head -20 "$src_md" | grep '^#[^#]' | head -1 | sed 's/^#[[:space:]]*//')
    
    if [[ "$section_type" == "workshops" ]]; then
      # For workshops, use chapter numbering starting from 0
      if [[ "$filename" == "chapter0" ]]; then
        echo "\\chapter{$title}" > "$temp_md"
      elif [[ "$filename" =~ ^chapter([0-9]+) ]]; then
        echo "\\chapter{$title}" > "$temp_md"
      elif [[ "$filename" =~ ^chapter([0-9]+)-([0-9]+) ]]; then
        # For sub-chapters like chapter3-1, use sections
        echo "\\section{$title}" > "$temp_md"
      else
        echo "\\chapter{$title}" > "$temp_md"
      fi
    else
      # For talks, treat each as a chapter
      echo "\\chapter{$title}" > "$temp_md"
    fi
    
    # Add content without the first heading (since we added chapter command)
    tail -n +2 "$src_md" | sed '/^#[^#]/d' >> "$temp_md"
    
    # Convert with mermaid filter if available
    if command -v mmdc >/dev/null 2>&1 && [[ -f "$lua_filter" ]]; then
      pandoc "$temp_md" -t latex -o "$out_tex" \
        --resource-path="$REPO_ROOT:$REPO_ROOT/docs:$REPO_ROOT/docs/assets/images:$REPO_ROOT/docs/talks:$REPO_ROOT/docs/workshops" \
        --lua-filter="$lua_filter"
    else
      pandoc "$temp_md" -t latex -o "$out_tex" \
        --resource-path="$REPO_ROOT:$REPO_ROOT/docs:$REPO_ROOT/docs/assets/images:$REPO_ROOT/docs/talks:$REPO_ROOT/docs/workshops"
    fi
    
    rm "$temp_md"
    
  done < "$list_file"
}

build_pdf_and_tex() {
  # $1: input md
  # $2: output stem (without extension)
  local in_md="$1"
  local out_stem="$2"

  local pdf_engine="--pdf-engine=tectonic"
  if ! command -v tectonic >/dev/null 2>&1; then
    # Fall back to default engine
    pdf_engine=""
  fi

  # Produce LaTeX
  pandoc "$in_md" -s -t latex -o "${out_stem}.tex" \
    --toc --toc-depth=2 \
    -V geometry:margin=1in \
    -V documentclass=book \
    -V classoption=oneside \
    -V urlcolor=blue \
    -V linkcolor=blue \
    -V colorlinks=true \
    --resource-path="$REPO_ROOT:$REPO_ROOT/docs:$REPO_ROOT/docs/assets/images:$REPO_ROOT/docs/talks:$REPO_ROOT/docs/workshops"

  # Produce PDF
  pandoc "$in_md" -s -o "${out_stem}.pdf" \
    --toc --toc-depth=2 \
    -V geometry:margin=1in \
    -V documentclass=book \
    -V classoption=oneside \
    -V urlcolor=blue \
    -V linkcolor=blue \
    -V colorlinks=true \
    --resource-path="$REPO_ROOT:$REPO_ROOT/docs:$REPO_ROOT/docs/assets/images:$REPO_ROOT/docs/talks:$REPO_ROOT/docs/workshops" \
    $pdf_engine
}

main() {
  if [[ "${EBOOK_SKIP_PDF:-}" != "1" ]]; then
    check_deps
  else
    echo "EBOOK_SKIP_PDF=1 → Skipping PDF/LaTeX build; assembling Markdown only" >&2
  fi

  local workshops_index="$WORKSHOPS_DIR/index.md"
  local talks_index="$TALKS_DIR/index.md"

  if [[ ! -f "$workshops_index" ]]; then
    echo "Missing $workshops_index" >&2
    exit 1
  fi
  if [[ ! -f "$talks_index" ]]; then
    echo "Missing $talks_index" >&2
    exit 1
  fi

  local all_md="$EBOOK_DIR/book_all.md"

  local src_base="$EBOOK_DIR/src"
  local tex_base="$EBOOK_DIR/tex"
  local workshops_src="$src_base/workshops"
  local talks_src="$src_base/talks"
  local workshops_tex="$tex_base/workshops"
  local talks_tex="$tex_base/talks"
  local workshops_list="$EBOOK_DIR/workshops_files.txt"
  local talks_list="$EBOOK_DIR/talks_files.txt"

  echo "Preparing workshops (src mirror)…"
  parse_and_prepare "$workshops_index" "$WORKSHOPS_DIR" "$workshops_src" "$workshops_list"
  echo "Preparing talks (src mirror)…"
  parse_and_prepare "$talks_index" "$TALKS_DIR" "$talks_src" "$talks_list"

  if [[ "${EBOOK_SKIP_PDF:-}" != "1" ]]; then
    echo "Converting workshops to LaTeX mirror…"
    convert_src_to_tex "$workshops_src" "$workshops_tex" "$workshops_list" "workshops"
    echo "Converting talks to LaTeX mirror…"
    convert_src_to_tex "$talks_src" "$talks_tex" "$talks_list" "talks"
  fi

  echo "Assembling concatenated Markdown (also available separately)…"
  {
    echo "---"
    echo "title: \"Systematically Improving RAG — Collected Edition\""
    echo "date: \"$(date '+%B %Y')\""
    echo "---"
    echo
    echo "# Systematically Improving RAG — Collected Edition"
    echo
    echo "\\tableofcontents"
    echo
    echo "\\newpage"
    # Compose markdown from src mirrors for convenience
    # Title pages for sections
    echo "# Workshops"
    echo
    # concatenate each in order
    while IFS= read -r f; do
      [[ -z "$f" ]] && continue
      rel="${f#$WORKSHOPS_DIR/}"
      cat "$workshops_src/$rel"
      echo
      echo "\\newpage"
    done < "$workshops_list"
    echo "\\newpage"
    echo "# Talks and Presentations"
    echo
    while IFS= read -r f; do
      [[ -z "$f" ]] && continue
      rel="${f#$TALKS_DIR/}"
      cat "$talks_src/$rel"
      echo
      echo "\\newpage"
    done < "$talks_list"
  } > "$all_md"

  if [[ "${EBOOK_SKIP_PDF:-}" != "1" ]]; then
    echo "Generating master LaTeX that includes per-file .tex…"
    local master_tex="$EBOOK_DIR/systematically_improving_rag_book.tex"
    
    # Check if master_tex already exists and has been manually modified
    if [[ -f "$master_tex" ]]; then
      echo "Master LaTeX file already exists. Preserving manual modifications."
      echo "To regenerate from template, delete: $master_tex"
    else
    {
      cat <<'LATEX'
\documentclass[11pt,twoside,openright]{book}

% Academic page setup
\usepackage[inner=1.5in,outer=1in,top=1.25in,bottom=1.25in,bindingoffset=0.2in]{geometry}
\usepackage{microtype}
\usepackage{setspace}
\onehalfspacing

% Academic typography
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{mathptmx}  % Times Roman with math support
\usepackage{helvet} % Helvetica for sans serif
\usepackage{courier} % Courier for monospace
\renewcommand{\sfdefault}{phv}
\renewcommand{\ttdefault}{pcr}

% Academic bibliography and citations
\usepackage[style=numeric,backend=biber,sorting=none]{biblatex}
\usepackage{csquotes}

% Enhanced math support
\usepackage{amsmath,amssymb,amsthm}
\usepackage{mathtools}

% Colors and links
\usepackage{xcolor}
\definecolor{bookblue}{RGB}{0,102,204}
\definecolor{bookgray}{RGB}{95,95,95}
\definecolor{codebg}{RGB}{248,249,250}

\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=bookblue,
    urlcolor=bookblue,
    citecolor=bookblue,
    filecolor=bookblue,
    pdftitle={Systematically Improving RAG Applications},
    pdfauthor={Jason Liu and Contributors},
    pdfsubject={Retrieval-Augmented Generation, Machine Learning, AI Engineering},
    pdfkeywords={RAG, Machine Learning, AI, Evaluation, Fine-tuning}
}

% Enhanced code formatting
\usepackage{listings}
\usepackage{fancyvrb}

% Native LaTeX diagram packages (alternatives to Mermaid)
\usepackage{tikz}
\usepackage{pgfplots}
\usetikzlibrary{shapes,arrows,positioning,fit,calc,decorations.pathreplacing}
\pgfplotsset{compat=1.18}
\lstset{
    backgroundcolor=\color{codebg},
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    frameround=tttt,
    rulecolor=\color{bookgray!30},
    numbers=none,
    numberstyle=\tiny\color{bookgray},
    keywordstyle=\color{bookblue}\bfseries,
    commentstyle=\color{bookgray}\itshape,
    stringstyle=\color{red!80!black},
    showstringspaces=false,
    tabsize=2,
    captionpos=b
}

% Academic section formatting
\usepackage{titlesec}
\titleformat{\chapter}[display]
  {\normalfont\Large\bfseries\centering}
  {\MakeUppercase{\chaptertitlename}\ \thechapter}{12pt}{\Large\MakeUppercase}
\titlespacing*{\chapter}{0pt}{-30pt}{40pt}

\titleformat{\section}
  {\normalfont\large\bfseries}
  {\thesection}{1em}{}
\titleformat{\subsection}
  {\normalfont\normalsize\bfseries}
  {\thesubsection}{1em}{}
\titleformat{\subsubsection}
  {\normalfont\normalsize\itshape}
  {\thesubsubsection}{1em}{}

% Academic theorem environments
\theoremstyle{definition}
\newtheorem{definition}{Definition}[section]
\newtheorem{example}{Example}[section]
\newtheorem{remark}{Remark}[section]

\theoremstyle{plain}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{lemma}{Lemma}[section]
\newtheorem{proposition}{Proposition}[section]
\newtheorem{corollary}{Corollary}[section]

% Enhanced quote formatting for admonitions
\usepackage{mdframed}
\newmdenv[
  leftmargin=10pt,
  rightmargin=10pt,
  skipabove=12pt,
  skipbelow=12pt,
  linecolor=bookblue,
  linewidth=2pt,
  topline=false,
  bottomline=false,
  rightline=false,
  backgroundcolor=bookblue!5
]{bookquote}

% Pandoc compatibility
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\providecommand{\passthrough}[1]{#1}
\providecommand{\pandocbounded}[1]{#1}

% Define Shaded environment for code blocks
\usepackage{framed}
\definecolor{shadecolor}{RGB}{248,249,250}
\newenvironment{Shaded}{\begin{snugshade}}{\end{snugshade}}

% Define Highlighting environment
\newenvironment{Highlighting}{}{}
\newcommand{\AlertTok}[1]{\textcolor[rgb]{1.00,0.00,0.00}{\textbf{#1}}}
\newcommand{\AnnotationTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textbf{\textit{#1}}}}
\newcommand{\AttributeTok}[1]{\textcolor[rgb]{0.77,0.63,0.00}{#1}}
\newcommand{\BaseNTok}[1]{\textcolor[rgb]{0.00,0.00,0.81}{#1}}
\newcommand{\BuiltInTok}[1]{#1}
\newcommand{\CharTok}[1]{\textcolor[rgb]{0.31,0.60,0.02}{#1}}
\newcommand{\CommentTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textit{#1}}}
\newcommand{\CommentVarTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textbf{\textit{#1}}}}
\newcommand{\ConstantTok}[1]{\textcolor[rgb]{0.00,0.00,0.00}{#1}}
\newcommand{\ControlFlowTok}[1]{\textcolor[rgb]{0.13,0.29,0.53}{\textbf{#1}}}
\newcommand{\DataTypeTok}[1]{\textcolor[rgb]{0.13,0.29,0.53}{#1}}
\newcommand{\DecValTok}[1]{\textcolor[rgb]{0.00,0.00,0.81}{#1}}
\newcommand{\DocumentationTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textbf{\textit{#1}}}}
\newcommand{\ErrorTok}[1]{\textcolor[rgb]{1.00,0.00,0.00}{\textbf{#1}}}
\newcommand{\ExtensionTok}[1]{#1}
\newcommand{\FloatTok}[1]{\textcolor[rgb]{0.00,0.00,0.81}{#1}}
\newcommand{\FunctionTok}[1]{\textcolor[rgb]{0.00,0.00,0.00}{#1}}
\newcommand{\ImportTok}[1]{#1}
\newcommand{\InformationTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textbf{\textit{#1}}}}
\newcommand{\KeywordTok}[1]{\textcolor[rgb]{0.13,0.29,0.53}{\textbf{#1}}}
\newcommand{\NormalTok}[1]{#1}
\newcommand{\OperatorTok}[1]{\textcolor[rgb]{0.81,0.36,0.00}{\textbf{#1}}}
\newcommand{\OtherTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{#1}}
\newcommand{\PreprocessorTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textit{#1}}}
\newcommand{\RegionMarkerTok}[1]{#1}
\newcommand{\SpecialCharTok}[1]{\textcolor[rgb]{0.00,0.00,0.00}{#1}}
\newcommand{\SpecialStringTok}[1]{\textcolor[rgb]{0.31,0.60,0.02}{#1}}
\newcommand{\StringTok}[1]{\textcolor[rgb]{0.31,0.60,0.02}{#1}}
\newcommand{\VariableTok}[1]{\textcolor[rgb]{0.00,0.00,0.00}{#1}}
\newcommand{\VerbatimStringTok}[1]{\textcolor[rgb]{0.31,0.60,0.02}{#1}}
\newcommand{\WarningTok}[1]{\textcolor[rgb]{0.56,0.35,0.01}{\textbf{\textit{#1}}}}

% Table formatting
\usepackage{booktabs}
\usepackage{array}
\usepackage{longtable}

% Graphics and figures
\usepackage{graphicx}
\usepackage{float}
\usepackage{wrapfig}  % For text wrapping around figures
\usepackage{subcaption}  % For subfigures
\usepackage{adjustbox}  % For resizing boxes/figures
\graphicspath{{../docs/assets/images/}{images/}}

% Better figure positioning
\makeatletter
\def\fps@figure{htbp}
\def\fps@table{htbp}
\makeatother

% Center figures by default
\makeatletter
\g@addto@macro\@floatboxreset\centering
\makeatother

% Academic headers and footers
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\small\itshape\leftmark}
\fancyhead[RO]{\small\itshape\rightmark}
\fancyhead[LO,RE]{\small\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Chapter page style
\fancypagestyle{plain}{%
  \fancyhf{}
  \fancyfoot[C]{\thepage}
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0pt}
}

% Academic title page
\title{
    \vspace{3cm}
    {\LARGE\bfseries SYSTEMATICALLY IMPROVING}\\[0.3cm]
    {\LARGE\bfseries RAG APPLICATIONS}\\[1.5cm]
    {\large A Comprehensive Guide to Building and Optimizing}\\[0.2cm]
    {\large Production-Ready Retrieval-Augmented Generation Systems}
}
\author{
    {\large Jason Liu}\\[1cm]
    {\normalsize with contributions from industry practitioners at}\\
    {\normalsize Zapier, ChromaDB, Glean, LanceDB, and other organizations}
}
\date{\today}

\begin{document}

% Title page
\maketitle
\thispagestyle{empty}

% Academic copyright page
\newpage
\thispagestyle{empty}
\vspace*{\fill}
\begin{center}
\small
\textcopyright\ 2024 Jason Liu and Contributors\\[2em]

This work is licensed under a Creative Commons Attribution 4.0 International License.\\
You are free to share and adapt this material for any purpose, even commercially,\\
provided appropriate credit is given.\\[2em]

Published by the author\\[1em]

For updates and additional resources:\\
\url{https://improvingrag.com}\\[2em]

First Edition, \today
\end{center}
\vspace*{\fill}

% Table of contents
\newpage
\tableofcontents

% List of figures (if any)
\cleardoublepage
\phantomsection
\addcontentsline{toc}{chapter}{List of Figures}
\listoffigures

% Abstract or Preface
\cleardoublepage
\phantomsection
\addcontentsline{toc}{chapter}{Preface}
\chapter*{Preface}

This book presents a systematic approach to building and improving Retrieval-Augmented Generation (RAG) applications in production environments. Rather than focusing solely on theoretical concepts, this work emphasizes practical methodologies for creating RAG systems that continuously improve through user feedback and data-driven optimization.

The content is organized into two complementary sections: structured workshops that guide readers through hands-on implementation, and expert presentations that provide real-world insights from practitioners at leading technology companies. Together, these materials offer both foundational knowledge and advanced techniques for building robust, scalable RAG systems.

% Main content
\cleardoublepage
\part{Workshops}
\setcounter{chapter}{-1}  % Start workshops from Chapter 0
LATEX
      while IFS= read -r f; do
        [[ -z "$f" ]] && continue
        rel="${f#$WORKSHOPS_DIR/}"
        incpath="tex/workshops/${rel%.md}"
        echo "\\include{$incpath}"
      done < "$workshops_list"
      cat <<'LATEX'

\part{Talks and Presentations}
LATEX
      while IFS= read -r f; do
        [[ -z "$f" ]] && continue
        rel="${f#$TALKS_DIR/}"
        incpath="tex/talks/${rel%.md}"
        echo "\\include{$incpath}"
      done < "$talks_list"
      cat <<'LATEX'

\end{document}
LATEX
    } > "$master_tex"
    fi  # End of master_tex generation check

    echo "Building PDFs and LaTeX into ${EBOOK_DIR}..."
    # Also produce concatenated pandoc builds (legacy)
    build_pdf_and_tex "$all_md" "${EBOOK_DIR}/systematically_improving_rag_book"
    # Compile master_tex via tectonic if available
    if command -v tectonic >/dev/null 2>&1; then
      (cd "$EBOOK_DIR" && tectonic -X compile --keep-intermediates --print --reruns 1 systematically_improving_rag_book.tex | cat)
    else
      echo "tectonic not installed; skipped compiling master include-based .tex" >&2
    fi
  else
    echo "Skipping PDF/LaTeX generation. Per-file mirrors in:"
    echo "  $src_base (processed Markdown)"
    echo "  $tex_base (LaTeX)"
  fi

  echo "Done. Outputs in: ${EBOOK_DIR}"
}

main "$@"