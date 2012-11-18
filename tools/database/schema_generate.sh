#! /bin/sh

pg_dump -s -O -x -t "marker*|dynpoi_categ|dynpoi_class|dynpoi_item|dynpoi_source|dynpoi_stats|dynpoi_status|dynpoi_update|dynpoi_update_last" osmose > schema.sql
