#! /bin/bash

set -e

DATABASE=osmose_frontend

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
