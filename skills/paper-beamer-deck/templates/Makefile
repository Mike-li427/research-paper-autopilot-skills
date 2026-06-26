# =============================================================================
# Makefile — build one Beamer deck with XeLaTeX + a fail-on-warning gate
#
# Copy into:  ./slides/<paper-short-name>/Makefile  (next to main.tex)
#
# Targets:
#   make            compile main.tex twice, then run the log gate (default)
#   make clean      remove LaTeX aux files
#   make distclean  also remove main.pdf
#   make check-log  run only the log gate against main.log
#
# Path assumptions:
#   - Deck lives at <workspace>/slides/<paper-short-name>/
#   - Theme .sty lives at <workspace>/  -> TEXINPUTS adds ../../ so xelatex
#     finds beamerthemeSimple.sty. main.tex's \graphicspath finds local figures/.
#
# The log gate prefers scripts/check_latex_log.py from the paper-beamer-deck
# skill; if that script is not reachable, it falls back to an inline grep gate.
# =============================================================================

TEX = main.tex
PDF = main.pdf
LOG = main.log

LATEX = xelatex
LATEX_FLAGS = -interaction=nonstopmode -halt-on-error

# Make the workspace root visible so the theme .sty is found.
export TEXINPUTS := ../../:$(TEXINPUTS)

# Try to locate the skill's log-checker. Override on the command line if needed:
#   make CHECK_LOG=/path/to/check_latex_log.py
CHECK_LOG ?= $(firstword $(wildcard \
	../../skills/paper-beamer-deck/scripts/check_latex_log.py \
	../../../skills/paper-beamer-deck/scripts/check_latex_log.py))

.PHONY: all clean distclean check-log

all: $(PDF) check-log

$(PDF): $(TEX)
	$(LATEX) $(LATEX_FLAGS) $(TEX)
	$(LATEX) $(LATEX_FLAGS) $(TEX)

check-log:
	@if [ -n "$(CHECK_LOG)" ] && [ -f "$(CHECK_LOG)" ]; then \
		python3 "$(CHECK_LOG)" $(LOG); \
	else \
		echo "(check_latex_log.py not found; using inline grep gate)"; \
		if grep -E "Overfull \\\\[hv]box|LaTeX Error|Package .* Error|File .* not found|undefined references|Citation .* undefined|Reference .* undefined" $(LOG); then \
			echo ""; \
			echo "ERROR: LaTeX layout, reference, or missing-file problem detected."; \
			echo "Fix the slide deck before accepting it."; \
			exit 1; \
		fi; \
	fi

clean:
	rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb *.fls *.fdb_latexmk *.synctex.gz

distclean: clean
	rm -f $(PDF)
