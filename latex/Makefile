PYTHON ?= python
LATEXMK ?= latexmk
export PYTHONPATH := $(abspath ../src):$(PYTHONPATH)

FIGURE_NUMBERS := 01 02 03 04 05 06 07 08 09 10 11 12 13
PAPER_ASSETS := $(foreach n,$(FIGURE_NUMBERS),../figures/paper/figure$(n).pdf) ../figures/paper/figure_statistics.tex

.PHONY: all check-figures figures refresh full-data

all: check-figures
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex

check-figures:
	@for asset in $(PAPER_ASSETS); do \
		if [ ! -f "$$asset" ]; then \
			printf '%s\n' "Missing saved paper asset: $$asset. Run 'make -C latex figures' from the repository root."; \
			exit 1; \
		fi; \
	done

figures:
	cd .. && $(PYTHON) -m bml figures all --output figures/outputs --update
	cd .. && $(PYTHON) -m bml save-paper-figures

refresh:
	cd .. && $(PYTHON) -m bml refresh-data --max-n 999

full-data:
	cd .. && $(PYTHON) -m bml refresh-data --max-n 10000 --skip-states
