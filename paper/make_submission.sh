#!/bin/sh
# Build the manuscript and collect the files for upload (source, style files, figures, tables, bibliography, compiled PDF).
set -e
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode main_sn.tex >/dev/null
bibtex main_sn >/dev/null
pdflatex -interaction=nonstopmode main_sn.tex >/dev/null
pdflatex -interaction=nonstopmode main_sn.tex >/dev/null
rm -f submission_package.zip
zip -qr submission_package.zip main_sn.tex main_sn.pdf main_sn.bbl references.bib sn-jnl.cls sn-basic.bst sections figures tables
echo "wrote submission_package.zip"
