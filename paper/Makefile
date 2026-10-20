PYTHON ?= python
LATEXMK ?= latexmk
export PYTHONPATH := $(abspath ../src):$(PYTHONPATH)

.PHONY: all figures refresh full-data

all: figures
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex

figures:
	cd .. && $(PYTHON) -m bml figures all --output paper/generated --update

refresh:
	cd .. && $(PYTHON) -m bml refresh-data --max-n 999

full-data:
	cd .. && $(PYTHON) -m bml refresh-data --max-n 10000 --skip-states
