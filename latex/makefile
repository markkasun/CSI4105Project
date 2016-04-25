MAIN=main
TARGET=Proposal
BIB=$(TARGET)
BIBDIR=ref
CLEANEXT=aux toc lof idx ilg ind log bbl bcf ist blg run.xml out pdf
MOVE := $(addprefix move,${CLEANEXT})

# You want latexmk to *always* run, because make does not have all the info.
# Also, include non-file targets in .PHONY so they are run regardless of any
# file of the given name existing.
.PHONY: convert auxilliary all clean ${MOVE}

# The first rule in a Makefile is the one executed by default ("make"). It
# should always be the "all" rule, so that "make" and "make all" are identical.
all: $(TARGET)/$(TARGET).pdf clean

# Expect user to generate $(TARGET)/$(TARGET).tex before running make
$(TARGET)/$(TARGET).pdf: auxilliary $(MAIN).tex $(TARGET)/$(TARGET).tex
# 	latexmk -pdf -pdflatex="pdflatex --interactive=nonstopmode --shell-escape %O %S" -use-make $(MAIN).tex
	arara $(MAIN).tex --log;
	cp $(MAIN).pdf $(TARGET)/$(TARGET).pdf

auxilliary:
	echo "\def\target{$(TARGET)/$(TARGET).tex}">build_aux.tex ;
	for file in $(BIB) ; do echo "\addbibresource{$(BIBDIR)/""$$file".bib"}">>build_aux.tex ; done ;

convert: $(TARGET)/$(TARGET).pdf
	./convert $(TARGET)

# % is wildcard. Redirect stderr and return true to supress errors; alternatively prefix - to command (";" -> "; -" ) to report errors but ignore.
${MOVE}: move%: ; mv -f *$* cleanup 2>/dev/null; true

clean: ${MOVE}
	
