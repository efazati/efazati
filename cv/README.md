# Resume / CV

Source files for Mohammad Efazati's resume. Compiles to a 2-page PDF.

## Files

| File | Purpose |
|---|---|
| `resume.tex` | LaTeX source (canonical for the PDF) |
| `Mohammad-Efazati-Resume.md` | Markdown mirror of the content (for reading on GitHub, ATS plain-text use) |
| `Mohammad-Efazati-Resume-v2.1.0.pdf` | Compiled output |
| `build.sh` | Rebuild script |
| `../assets/Mohammad-Efazati-CV.pdf` | Mirror copy that the website's "Download CV" link points to |

## How it's built

```bash
./build.sh
```

The script runs `pdflatex` twice (for cross-references), then copies the resulting PDF to both the versioned filename and the website's `assets/` folder.

## Tooling and font

- **Compiler:** `pdflatex` from TeX Live
- **Font:** **Computer Modern Sans Serif** (`cmss`) - the default sans-serif of the Computer Modern family that ships with `texlive-basic`. It's a clean geometric sans that renders consistently and, crucially, embeds proper ToUnicode CMaps so the text is **extractable by ATS systems and screen readers**.
- **Why not Helvetica or TeX Gyre Heros?** Those produce nicer-looking PDFs but my local install couldn't generate text-extractable output via `lualatex + fontspec` (text rendered visually but `pdftotext` returned empty). For a resume, ATS-friendly text extraction beats prettier typography.

## LaTeX packages used

```
fontspec-free defaults  (cmss family)
geometry                margins
xcolor                  5-color palette (deep teals + warm amber)
enumitem                compact bullet lists
hyperref                clickable links
parskip                 paragraph spacing
paracol                 two-column layout (sidebar + main)
calc                    layout arithmetic
hyphenat                disable line-end word hyphenation
needspace               widow protection (keeps role title with body)
fancyhdr                page style
```

All available from `texlive-basic` + `texlive-latex` + `texlive-latexrecommended`.

## Color palette

Five harmonious teal-emerald shades plus one warm amber for highlights:

| Token | Hex | Role |
|---|---|---|
| `c1` | `#064E3B` | section heading text (deepest emerald) |
| `c2` | `#115E59` | company names, primary accent |
| `c3` | `#0D9488` | hyperlinks |
| `c4` | `#14B8A6` | sidebar rule lines |
| `c5` | `#99F6E4` | reserved |
| `warm` | `#B45309` | position titles, version label |

Plus standard grays (`ink #0F172A`, `ink2 #1E293B`, `muted #475569`, `mutedLight #94A3B8`, `rule #CBD5E1`).

## Editing notes

- `resume.tex` is the source of truth for the PDF.
- `Mohammad-Efazati-Resume.md` should be kept in sync manually when content changes.
- Version label is in two places: the `\fancyfoot` rule in `resume.tex` (`RESUME V2.1.0`) and the filename suffix `v2.1.0`. Bump both when releasing.
