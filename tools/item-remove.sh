#! /bin/bash

for i in $*; do
  echo -n "$i "
  psql -d osmose_frontend --tuples-only -c "SELECT count(*) FROM marker WHERE item = '$i'"

  echo "confirm?"
  read ln

  psql -d osmose_frontend -c  "DELETE FROM marker where item = '$i'"
  psql -d osmose_frontend -c  "DELETE FROM class where item = '$i'"
  psql -d osmose_frontend -c  "DELETE FROM items where item = '$i'"
done
