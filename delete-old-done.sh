#! /bin/sh
psql -d osmose -c "delete from dynpoi_status where date < now()-interval '7 day' and status = 'done';" osmose
