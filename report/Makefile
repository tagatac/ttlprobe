date = $(shell date '+%Y%m%d')
SECTIONS = main abstr intro prep gfwprobe gcprobe rslts future concln
PLOTS = histhomepages histhomepages-mod histfull histfull-mod
JPGS = gfwfalun gfwtest
PNGS = gfwbaiduip $(PLOTS)

$(date)TTLProbe.pdf : $(SECTIONS:=.tex) $(addprefix figures/, $(JPGS:=.jpg)) $(addprefix figures/, $(PNGS:=.png)) refs.bib
	pdflatex -draftmode -jobname $(date)TTLProbe main.tex
	bibtex $(date)TTLProbe
	pdflatex -draftmode -jobname $(date)TTLProbe main.tex
	pdflatex -jobname $(date)TTLProbe main.tex

figures/histhomepages.png : ../results/best/gcprobe.json scripts/gen_plot.py
	scripts/gen_plot.py $< $@

figures/histhomepages-mod.png : ../results/best/modified.json scripts/gen_plot.py
	scripts/gen_plot.py $< $@

figures/histfull.png : ../results/20150818T1418-memfailfiles/gcprobe.json scripts/gen_plot.py
	scripts/gen_plot.py $< $@

figures/histfull-mod.png : ../results/20150818T1418-memfailfiles/modified.json scripts/gen_plot.py
	scripts/gen_plot.py $< $@


.PHONY : clean

clean :
	rm -vf *TTLProbe.pdf *.aux *.log *.out *.ent *.bbl *.blg $(addprefix figures/, $(PLOTS:=.png))
