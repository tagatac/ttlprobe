date = $(shell date '+%Y%m%d')
SECTIONS = report abstr intro prep gfwprobe gcprobe rslts future concln
FIGURES = 

$(date)TimeRandomization.pdf : $(SECTIONS:=.tex) $(addprefix figures/, $(FIGURES:=.png)) refs.bib
	pdflatex -draftmode -jobname $(date)TTLProbe report.tex
	bibtex $(date)TTLProbe
	pdflatex -draftmode -jobname $(date)TTLProbe report.tex
	pdflatex -jobname $(date)TTLProbe report.tex

.PHONY : clean

clean :
	rm -vf *TTLProbe.pdf *.aux *.log *.out *.ent *.bbl *.blg
