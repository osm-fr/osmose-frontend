#! /bin/bash

set -e

DATABASE=osmose_frontend
DIR_DUMP="/data/work/$(whoami)/"

psql -d $DATABASE -c "DELETE FROM dynpoi_status WHERE date < now()-interval '7 day' AND status = 'done';"

psql -d $DATABASE -c "INSERT INTO dynpoi_stats (SELECT dynpoi_class.source, dynpoi_class.class, now(), count(marker.source) FROM dynpoi_class LEFT JOIN marker ON dynpoi_class.source=marker.source AND dynpoi_class.class=marker.class GROUP BY dynpoi_class.source, dynpoi_class.class);"

psql -d $DATABASE -c "UPDATE dynpoi_item SET levels = (SELECT array_agg(level)
              FROM (SELECT level FROM dynpoi_class
                    WHERE dynpoi_class.item = dynpoi_item.item
                    GROUP BY level
                    ORDER BY level
                   ) AS a
             );"

psql -d $DATABASE -c "UPDATE dynpoi_item SET number = (SELECT array_agg(n)
              FROM (SELECT count(*) AS n FROM marker
                    JOIN dynpoi_class ON dynpoi_class.source = marker.source AND
                                         dynpoi_class.class = marker.class
                    WHERE dynpoi_class.item = dynpoi_item.item
                    GROUP BY level
                    ORDER BY level
                   ) AS a
             );"

psql -d $DATABASE -c "UPDATE dynpoi_item SET tags = (SELECT array_agg(tag)
              FROM (
                SELECT
                    tag
                FROM
                    (SELECT unnest(tags) AS tag, item FROM dynpoi_class WHERE dynpoi_class.item = dynpoi_item.item) AS dynpoi_class
                WHERE
                    tag != ''
                GROUP BY tag
                ORDER BY tag
             ) AS a
             );"

mkdir "$DIR_DUMP/tmp"
mkdir "$DIR_DUMP/export"

pg_dump -t dynpoi_status_id_seq -t dynpoi_categ -t dynpoi_class -t dynpoi_item -t dynpoi_update_last -t marker -t marker_elem -t marker_fix -t source $DATABASE \
  | bzip2 > "$DIR_DUMP/tmp/osmose-planet-latest.sql.bz2.tmp"
mv "$DIR_DUMP/tmp/osmose-planet-latest.sql.bz2.tmp" "$DIR_DUMP/export/osmose-planet-latest.sql.bz2"
