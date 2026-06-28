# LaTeX Submission Package

Canonical files:

- `main.tex`
- `refs.bib`
- `colm2026_conference.sty`
- `colm2026_conference.bst`
- `fancyhdr.sty`
- `natbib.sty`
- `math_commands.tex`
- `colm2026_conference.pdf`

Build command:

```bash
make
```

This package is rebased on `Template-2026.zip` and includes the local COLM 2026 template support files. The checked-in `colm2026_conference.sty`, `colm2026_conference.bst`, `fancyhdr.sty`, `natbib.sty`, `math_commands.tex`, and `colm2026_conference.pdf` files were compared byte-for-byte against the supplied template archive on 2026-06-28. The SVG figures in `../figures/` remain available for later camera-ready polish, but this LaTeX draft is self-contained and compileable without SVG conversion.

Verified on 2026-06-28:

- `conda run -n ask_guess python -m unittest discover -s tests`
- `latexmk -pdf -interaction=nonstopmode main.tex`
- output: `main.pdf`, 12 pages
- no unresolved references or citations in the final log

Reproducibility manifest:

- `../reproducibility.md`
- safe cached API replay uses `src/run_api_experiment.py --cache-only`
