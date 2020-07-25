#! /bin/bash

for i in $*; do
  echo -n "$i"
  psql -d osmose_frontend --tuples-only -c "SELECT count(*) FROM sources WHERE country = '$i'"

  echo "confirm?"
  read ln

  psql -d osmose_frontend -c  "DELETE FROM marker
                      WHERE source IN (SELECT id FROM sources WHERE country = '$i');"
  psql -d osmose_frontend -c  "DELETE FROM updates_last
                      WHERE source IN (SELECT id FROM sources WHERE country = '$i');"
  psql -d osmose_frontend -c  "DELETE FROM dynpoi_class
                      WHERE source IN (SELECT id FROM sources WHERE country = '$i');"
  psql -d osmose_frontend -c  "DELETE FROM markers_status
                      WHERE source_id IN (SELECT id FROM sources WHERE country = '$i');"
  psql -d osmose_frontend -c  "DELETE FROM sources_password
                      WHERE source_id IN (SELECT id FROM sources WHERE country = '$i');"

done
