
PYFILES=$(shell find .. -name '*.py' -not -type l | sort)
TPLFILES=$(shell find ../views -name '*.tpl' | sort)
LANG=fr en de nl it

MO=$(foreach l,$(LANG),mo/$(l)/LC_MESSAGES/osmose-frontend.mo)
PO=$(foreach l,$(LANG),$(l).po)

.PRECIOUS: $(PO) $(MO)

all: $(PO) $(MO)

tmp.tpl: $(TPLFILES)
	egrep -h "_\([\"']|TRANSLATORS" $(TPLFILES) | sed -e 's/.*_[(]"\([^"]\+\)"[)].*/_("\1")/g' -e "s/.*_[(]'\([^']\+\)'[)].*/_('\1')/g" -e 's/^%#/#/' > tmp.tpl

osmose-frontend.pot: $(PYFILES) tmp.tpl
	LANG=C xgettext -cTRANSLATORS --language=Python --keyword=_ --output=$@.tmp $(PYFILES) tmp.tpl
	diff -I ".*POT-Creation-Date:.*" $@ $@.tmp || cp $@.tmp $@

%.po: osmose-frontend.pot
	if test -e $@; then \
	  msgmerge -o $@ $@ $<; \
	else \
	  msginit --locale=$(patsubst %.po,%,$@) --input=$< --output=$@; \
	fi;

mo/%/LC_MESSAGES/osmose-frontend.mo: %.po
	@mkdir -p $(patsubst %/osmose-frontend.mo,%,$@)
	msgfmt --output-file=$@ $<

statistics:
	@for i in $(PO); do \
	  (msgfmt --statistics --verbose -o - $$i > /dev/null) 2>&1; \
	done
