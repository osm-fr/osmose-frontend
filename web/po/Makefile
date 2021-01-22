
PYFILES=$(shell find .. -name '*.py' -not -type l -not -path '*/externals/*' | sort)
TPLFILES=$(shell find ../views -name '*.tpl' | sort)
VUEFILES=$(shell find ../static -name '*.vue' | sort)
DBFILES=../../tools/database/categories_menu.txt ../../tools/database/items_menu.txt

PO:=$(wildcard *.po)
MO:=$(patsubst %.po,mo/%/LC_MESSAGES/osmose-frontend.mo,$(PO))

.PRECIOUS: $(PO) $(MO)

all: osmose-frontend.pot %.po mo

tmp.tpl: $(TPLFILES) Makefile
	cat $(TPLFILES) | \
	  perl -pe 's/(.*?)_[(] ?u?"([^"]+)"[)]/\1\n _("\2")\n/g' | \
	  perl -pe "s/(.*?)_[(] ?u?'([^']+)'[)]/\1\n _('\2')\n/g" | \
	  egrep -h "_\( ?u?[\"']|TRANSLATORS" | \
          sed -e 's/^%#/#/' > tmp.tpl

vue.pot: $(VUEFILES)
	../node_modules/easygettext/src/extract-cli.js --removeHTMLWhitespaces --attribute=path --output $@ $(VUEFILES)

python.pot: $(PYFILES) tmp.tpl $(DBFILES)
	sed -i "s/^#: .*//" osmose-frontend.pot
	LANG=C xgettext -cTRANSLATORS --language=Python \
          --keyword=_ --omit-header --from-code UTF-8 \
          --output=$@ $(PYFILES) tmp.tpl $(DBFILES)

osmose-frontend.pot: python.pot vue.pot
	msgcat python.pot vue.pot > $@

%.po:
	tx pull -a --minimum-perc=10

mo: $(MO)

mo/%/LC_MESSAGES/osmose-frontend.mo: %.po
	@mkdir -p $(patsubst %/osmose-frontend.mo,%,$@)
	msgfmt --output-file=$@ $<

statistics:
	@for i in $(PO); do \
	  (msgfmt --statistics --verbose -o - $$i > /dev/null) 2>&1; \
	done
