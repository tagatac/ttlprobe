date = $(shell date '+%Y%m%d')
SECTIONS = main abstr intro prep gfwprobe gcprobe rslts future concln
JPGS = gfwfalun gfwtest
PNGS = gfwbaiduip gcprobehist

$(date)TTLProbe.pdf : $(SECTIONS:=.tex) $(addprefix figures/, $(JPGS:=.jpg)) $(addprefix figures/, $(PNGS:=.png)) refs.bib
	pdflatex -draftmode -jobname $(date)TTLProbe main.tex
	bibtex $(date)TTLProbe
	pdflatex -draftmode -jobname $(date)TTLProbe main.tex
	pdflatex -jobname $(date)TTLProbe main.tex

figures/gcprobehist.png : ../results/best/gcprobe.json
	scripts/gen_plots.py

.PHONY : clean

clean :
	rm -vf *TTLProbe.pdf *.aux *.log *.out *.ent *.bbl *.blg
