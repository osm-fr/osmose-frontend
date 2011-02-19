#! /bin/sh
for t in dynpoi_source dynpoi_marker dynpoi_status dynpoi_update dynpoi_user
do
  echo $t
  psql -d osmose -c "UPDATE $t SET source=$2 WHERE source=$1;" osmose || exit 1
done
