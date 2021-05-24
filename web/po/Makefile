PYFILES=$(shell find ../../web_api -name '*.py' -not -type l -not -path '*/externals/*' | sort)
VUEFILES=$(shell find ../src -name '*.vue' | grep -v translate-slot.vue | sort)
DBFILES=../../tools/database/categories_menu.txt ../../tools/database/items_menu.txt

PO:=$(wildcard *.po)
MO:=$(patsubst %.po,mo/%/LC_MESSAGES/osmose-frontend.mo,$(PO))

.PRECIOUS: $(PO) $(MO)

all: osmose-frontend.pot %.po mo

vue.pot: $(VUEFILES)
	[ -f ../node_modules/easygettext/src/extract-cli.js ] || (echo 'easygettext missing. Please install node dependencies with `npm install --dev`' && exit 1)
	../node_modules/easygettext/src/extract-cli.js --removeHTMLWhitespaces --attribute=path --output $@.tmp $(VUEFILES)
	# extract header from original .pot, to get Content-Type=UTF-8
	sed -e '/^$$/q' osmose-frontend.pot > $@.tmp2
	# remove header from vue.pot
	sed -n '/^$$/,$$p' $@.tmp >> $@.tmp2
	mv $@.tmp2 $@
	rm $@.tmp

python.pot: $(PYFILES) $(DBFILES)
	sed -i "s/^#: .*//" osmose-frontend.pot
	LANG=C xgettext -cTRANSLATORS --language=Python \
          --keyword=_ --omit-header --from-code UTF-8 \
          --output=$@ $(PYFILES) $(DBFILES)

.PHONY: osmose-frontend.pot
osmose-frontend.pot: python.pot vue.pot
	sed '/^#\. #-#-#-#-#/d' $@ > $@.nofiles
	msgcat $@.nofiles python.pot vue.pot > $@.tmp
	mv $@.tmp $@
	rm $@.nofiles

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
