#! /bin/bash

for i in $*; do
  echo -n "$i "
  psql -d osmose_frontend --tuples-only -c "SELECT count(*) FROM markers WHERE item = '$i'"

  echo "confirm?"
  read ln

  psql -d osmose_frontend -c  "DELETE FROM markers_counts where item = '$i'"
  psql -d osmose_frontend -c  "DELETE FROM markers where item = '$i'"
  psql -d osmose_frontend -c  "DELETE FROM class where item = '$i'"
  psql -d osmose_frontend -c  "DELETE FROM items where item = '$i'"
done
