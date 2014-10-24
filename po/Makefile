
PYFILES=$(shell find .. -name '*.py' -not -type l -not -path '*/externals/*' | sort)
TPLFILES=$(shell find ../views -name '*.tpl' | sort)
DBFILES=../tools/database/categ_menu.txt ../tools/database/item_menu.txt

PO:=$(wildcard *.po)
MO:=$(patsubst %.po,mo/%/LC_MESSAGES/osmose-frontend.mo,$(PO))

.PRECIOUS: $(PO) $(MO)

all: osmose-frontend.pot %.po mo

tmp.tpl: $(TPLFILES)
	egrep -h "_\( ?u?[\"']|TRANSLATORS" $(TPLFILES) | \
	  perl -pe 's/.*?_[(] ?u?"([^"]+)"[)]/ _("\1") /g' | \
	  perl -pe "s/.*?_[(] ?u?'([^']+)'[)]/ _('\1') /g" | \
          sed -e 's/^%#/#/' > tmp.tpl

osmose-frontend.pot: $(PYFILES) tmp.tpl $(DBFILES)
	sed -i "s/^#: .*//" osmose-frontend.pot
	LANG=C xgettext --join-existing -cTRANSLATORS --language=Python \
          --keyword=_ --omit-header --from-code UTF-8 \
          --output=$@ $(PYFILES) tmp.tpl $(DBFILES)

%.po:
	tx pull -a --minimum-perc=30

mo: $(MO)

mo/%/LC_MESSAGES/osmose-frontend.mo: %.po
	@mkdir -p $(patsubst %/osmose-frontend.mo,%,$@)
	msgfmt --output-file=$@ $<

statistics:
	@for i in $(PO); do \
	  (msgfmt --statistics --verbose -o - $$i > /dev/null) 2>&1; \
	done
