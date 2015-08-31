date = $(shell date '+%Y%m%d')
SECTIONS = main abstr intro prep gfwprobe gcprobe rslts future concln
PLOTS = histtest histhomepages histmemfail
JPGS = gfwfalun gfwtest
PNGS = gfwbaiduip $(PLOTS)

$(date)TTLProbe.pdf : $(SECTIONS:=.tex) $(addprefix figures/, $(JPGS:=.jpg)) $(addprefix figures/, $(PNGS:=.png)) refs.bib
	pdflatex -draftmode -jobname $(date)TTLProbe main.tex
	bibtex $(date)TTLProbe
	pdflatex -draftmode -jobname $(date)TTLProbe main.tex
	pdflatex -jobname $(date)TTLProbe main.tex

figures/histtest.png : ../results/shortroutingtest-20150830T1830/gcprobe.json scripts/gen_plot.py
	scripts/gen_plot.py $< $@ False

figures/histhomepages.png : ../results/homepagefiles-20150817T2300/modified.json scripts/gen_plot.py
	scripts/gen_plot.py $< $@

figures/histmemfail.png : ../results/memfailfiles-20150818T1418/modified.json scripts/gen_plot.py
	scripts/gen_plot.py $< $@


.PHONY : clean

clean :
	rm -vf *TTLProbe.pdf *.aux *.log *.out *.ent *.bbl *.blg $(addprefix figures/, $(PLOTS:=.png))
