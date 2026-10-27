#!/usr/bin/env bash
# Build the manuscript: Markdown -> DOCX (pandoc) and -> PDF (pandoc HTML + headless Chromium).
set -euo pipefail
cd "$(dirname "$0")"
cat manuscript_part1.md manuscript_part2.md > manuscript.md
CHROME=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux*/chrome 2>/dev/null | head -1 || true)
pandoc manuscript.md --citeproc --bibliography references.bib --csl ieee.csl \
  --number-sections=false -o manuscript.docx
pandoc manuscript.md --citeproc --bibliography references.bib --csl ieee.csl \
  --standalone --mathml --css style.css --embed-resources -o manuscript.html
if [ -n "$CHROME" ]; then
  "$CHROME" --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
    --print-to-pdf=manuscript.pdf "file://$(pwd)/manuscript.html" 2>/dev/null
fi
wc -w manuscript.md
ls -la manuscript.docx manuscript.pdf 2>/dev/null || true
