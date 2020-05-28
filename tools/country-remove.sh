#! /bin/bash

for i in $*; do
  echo -n "$i"
  psql -d osmose_frontend --tuples-only -c "SELECT count(*) FROM source WHERE country = '$i'"

  echo "confirm?"
  read ln

  psql -d osmose_frontend -c  "DELETE FROM marker
                      WHERE source IN (SELECT id FROM source WHERE country = '$i');"
  psql -d osmose_frontend -c  "DELETE FROM dynpoi_update_last
                      WHERE source IN (SELECT id FROM source WHERE country = '$i');"
  psql -d osmose_frontend -c  "DELETE FROM dynpoi_class
                      WHERE source IN (SELECT id FROM source WHERE country = '$i');"
  psql -d osmose_frontend -c  "DELETE FROM dynpoi_status
                      WHERE source IN (SELECT id FROM source WHERE country = '$i');"
  psql -d osmose_frontend -c  "DELETE FROM source_password
                      WHERE source_id IN (SELECT id FROM source WHERE country = '$i');"

done
