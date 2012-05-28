#! /bin/sh

for i in item_menu*.txt; do
  echo $i
  lang=`echo $i | cut -d'_' -f3 | cut -d. -f1`
  cat $i | sed "s/'/''/g" | sed "s/ *\([0-9]*\) *| \(.*\)/update dynpoi_item set menu = coalesce(menu, hstore('$lang','')) || hstore('$lang', '\2') where item = \1;/" | psql osmose
done
