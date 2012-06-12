#! /bin/sh

for i in categ_menu*.txt; do
  echo $i
  lang=`echo $i | cut -d'_' -f3 | cut -d. -f1`
  cat $i | sed "s/'/''/g" | sed "s/ *\([0-9]*\) *| \(.*\)/update dynpoi_categ set menu = coalesce(menu, hstore('$lang','')) || hstore('$lang', '\2') where categ = \1;/" | psql osmose
done
