# Compilation des documents LaTeX
# Usage: make rapport | make presentation | make all

LATEX = pdflatex
RAPPORT = rapport
PRESENTATION = presentation

all: rapport presentation

rapport:
	$(LATEX) $(RAPPORT).tex
	$(LATEX) $(RAPPORT).tex

presentation:
	$(LATEX) $(PRESENTATION).tex
	$(LATEX) $(PRESENTATION).tex

clean:
	rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb *.bbl *.blg *.synctex.gz

.PHONY: all rapport presentation clean
