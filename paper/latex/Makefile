PDF=main.pdf

.PHONY: all clean

all: $(PDF)

$(PDF): main.tex refs.bib colm2026_conference.sty
	latexmk -pdf -interaction=nonstopmode main.tex

clean:
	latexmk -C main.tex
