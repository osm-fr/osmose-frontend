#! /bin/bash

for i in $*; do
  echo "$i "
  psql -d osmose_frontend --tuples-only -c "SELECT * FROM sources WHERE analyser = '$i'"

  echo "confirm?"
  read ln

  psql -d osmose_frontend -c  "DELETE FROM markers
                      WHERE source_id IN (SELECT id FROM sources WHERE analyser = '$i');"
  psql -d osmose_frontend -c  "DELETE FROM updates_last
                      WHERE source_id IN (SELECT id FROM sources WHERE analyser = '$i');"
  psql -d osmose_frontend -c  "DELETE FROM markers_counts
                      WHERE source_id IN (SELECT id FROM sources WHERE analyser = '$i');"
  psql -d osmose_frontend -c  "DELETE FROM markers_status
                      WHERE source_id IN (SELECT id FROM sources WHERE analyser = '$i');"
  psql -d osmose_frontend -c  "DELETE FROM sources_password
                      WHERE source_id IN (SELECT id FROM sources WHERE analyser = '$i');"
done
