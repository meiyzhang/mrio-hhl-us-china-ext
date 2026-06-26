.PHONY: all classical quantum figures paper clean

all: classical quantum figures

classical:
	cd src && python 01_load_eora.py && python 02_classical_mrio.py

quantum:
	cd src && python 03_build_subsystem.py && python 04_hhl_solve.py

figures:
	cd src && python 05_make_figures.py && python 06_make_schematics.py
	cp figures/fig_mrio_block.png figures/fig_hhl_pipeline.png \
	   figures/fig_complexity.png figures/fig_bilateral_full.png \
	   figures/fig_solution_compare.png figures/fig_policy_number.png paper/images/

paper:
	cd paper && pdflatex main.tex && pdflatex main.tex

clean:
	rm -rf results/cache
	rm -f paper/*.aux paper/*.log paper/*.out
