#! /bin/bash

item=$1
cl=$2

echo -n "$item - $cl "
psql -d osmose_frontend --tuples-only -c "SELECT count(*) FROM markers WHERE item = '$item' and class='$cl'"

echo "confirm?"
read ln

psql -d osmose_frontend -c  "DELETE FROM markers where item = '$item' and class='$cl'"
psql -d osmose_frontend -c  "DELETE FROM markers_counts where item = '$item' and class='$cl'"
psql -d osmose_frontend -c  "DELETE FROM markers_status where item = '$item' and class='$cl'"
psql -d osmose_frontend -c  "DELETE FROM class where item = '$item' and class='$cl'"
