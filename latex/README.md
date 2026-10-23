# Paper source

This directory is a standalone LaTeX project. It contains the manuscript,
bibliography, local preamble, appendices, thirteen saved figure PDFs and their
numerical caption values. It can be copied or uploaded without any other part
of the companion repository.

Compile from this directory with a standard TeX Live installation:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The result is `main.pdf`. Alternatively, use `latexmk -pdf main.tex`.
The included `main.bbl` contains the compiled bibliography, so repeated
PDFLaTeX runs also work without BibTeX until the references change.
Compilation uses the saved figures and catalogue; it runs no simulations or
Python code and requires no shell escape.

| File or directory | Contents |
| --- | --- |
| `main.tex` | Main manuscript |
| `preamble.sty` | Packages, mathematical notation and paper metadata |
| `refs.bib`, `main.bbl` | Editable references and compiled bibliography |
| `figure_statistics.tex` | Saved coefficients and sample ranges used in captions |
| `figures/` | The thirteen figure PDFs |
| `sections/` | Algorithm and periodic-tiling catalogue |

## Submission source

Upload the source files and saved figures, including `main.bbl`, with
`main.tex` at the archive root. Omit `main.pdf`, auxiliary files, logs and this
README. From this directory, a source archive can be created with:

```bash
zip -r ../miscellaneous/arxiv-source.zip main.tex preamble.sty refs.bib main.bbl figure_statistics.tex sections figures
```

See the [arXiv TeX submission instructions](https://info.arxiv.org/help/submit_tex.html)
for supported inputs and bibliography handling.
