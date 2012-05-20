#! /bin/sh

for i in item_menu*.txt; do
  echo $i
  cat $i | sed "s/'/''/g" | sed "s/ *\([0-9]*\) *| \(.*\)/update dynpoi_item set menu = menu || hstore('nl', '\2') where item = \1;/" | psql osmose
done
