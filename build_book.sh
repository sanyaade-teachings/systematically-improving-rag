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
    # Emoji fallbacks for LaTeX
    for a, b in {
        "✅": "[OK]",
        "❌": "[X]",
        "✔️": "[OK]",
        "✖️": "[X]",
        "🚀": "(rocket)",
        "💡": "(idea)",
        "📝": "(note)",
        "🔥": "(fire)",
    }.items():
        text = text.replace(a, b)
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
  local src_base="$1"
  local tex_base="$2"
  local list_file="$3"

  mkdir -p "$tex_base"

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
    pandoc "$src_md" -t latex -o "$out_tex" \
      --resource-path="$REPO_ROOT:$REPO_ROOT/docs:$REPO_ROOT/docs/assets/images:$REPO_ROOT/docs/talks:$REPO_ROOT/docs/workshops"
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
    convert_src_to_tex "$workshops_src" "$workshops_tex" "$workshops_list"
    echo "Converting talks to LaTeX mirror…"
    convert_src_to_tex "$talks_src" "$talks_tex" "$talks_list"
  fi

  echo "Assembling concatenated Markdown (also available separately)…"
  {
    echo "---"
    echo "title: Systematically Improving RAG — Collected Edition"
    echo "date: "
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
    {
      cat <<'LATEX'
\documentclass[oneside]{book}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{hyperref}
\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue}
\begin{document}
\tableofcontents
\clearpage
\part{Workshops}
LATEX
      while IFS= read -r f; do
        [[ -z "$f" ]] && continue
        rel="${f#$WORKSHOPS_DIR/}"
        incpath="tex/workshops/${rel%.md}"
        echo "\\include{$incpath}"
        echo "\\clearpage"
      done < "$workshops_list"
      cat <<'LATEX'
\part{Talks and Presentations}
LATEX
      while IFS= read -r f; do
        [[ -z "$f" ]] && continue
        rel="${f#$TALKS_DIR/}"
        incpath="tex/talks/${rel%.md}"
        echo "\\include{$incpath}"
        echo "\\clearpage"
      done < "$talks_list"
      cat <<'LATEX'
\end{document}
LATEX
    } > "$master_tex"

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