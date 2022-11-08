#! /bin/bash

item=$1
cl=$2
source=$3

echo -n "$item - $cl - $source"
psql -d osmose_frontend --tuples-only -c "SELECT count(*) FROM markers WHERE item = '$item' and class='$cl' and source_id='$source'"

echo "confirm?"
read ln

psql -d osmose_frontend -c  "DELETE FROM markers where item = '$item' and class='$cl' and source_id='$source'"
psql -d osmose_frontend -c  "DELETE FROM markers_counts where item = '$item' and class='$cl' and source_id='$source'"
psql -d osmose_frontend -c  "DELETE FROM updates_last WHERE source_id = '$source';"
