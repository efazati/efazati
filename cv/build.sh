#!/usr/bin/env bash
# Build the resume PDF from resume.tex using pdflatex.
# Also copies the PDF to ../assets/Mohammad-Efazati-CV.pdf for the website.

set -uo pipefail
cd "$(dirname "$0")"

VERSION="v2.1.0"
STEM="Mohammad-Efazati-Resume-${VERSION}"

# PDF via pdflatex (Computer Modern Sans; ATS-compatible text extraction)
pdflatex -interaction=nonstopmode resume.tex > /dev/null || true
pdflatex -interaction=nonstopmode resume.tex > /dev/null || true

if [[ ! -f resume.pdf ]]; then
    echo "ERROR: pdflatex failed to produce resume.pdf"
    exit 1
fi

cp resume.pdf "${STEM}.pdf"
cp resume.pdf ../assets/Mohammad-Efazati-CV.pdf

# Clean up auxiliary files
rm -f resume.aux resume.log resume.out resume.pdf

echo "Built ${STEM}.pdf"
pdfinfo "${STEM}.pdf" 2>/dev/null | grep -E "Pages|File size" || true
