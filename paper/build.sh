#!/usr/bin/env bash
# Build the manuscript: Markdown -> DOCX (pandoc) and -> PDF (pandoc HTML + headless Chromium).
set -euo pipefail
cd "$(dirname "$0")"
cat manuscript_part1.md manuscript_part2.md manuscript_part3.md > manuscript.md
CHROME=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux*/chrome 2>/dev/null | head -1 || true)
pandoc manuscript.md --citeproc --bibliography references.bib --csl ieee.csl \
  -o manuscript.docx
pandoc manuscript.md --citeproc --bibliography references.bib --csl ieee.csl \
  --standalone --mathml --css style.css --embed-resources -o manuscript.html
if [ -n "$CHROME" ]; then
  "$CHROME" --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
    --print-to-pdf=manuscript.pdf "file://$(pwd)/manuscript.html" 2>/dev/null
fi
pandoc supplementary.md --standalone --css style.css --embed-resources -o supplementary.html
pandoc supplementary.md -o supplementary.docx
if [ -n "$CHROME" ]; then
  "$CHROME" --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
    --print-to-pdf=supplementary.pdf "file://$(pwd)/supplementary.html" 2>/dev/null
fi
wc -w manuscript.md supplementary.md
ls -la manuscript.docx manuscript.pdf 2>/dev/null || true
