#! /bin/sh

pg_dump -s -O -x -t "marker*|dynpoi_categ|dynpoi_class|dynpoi_item|source|source_password|dynpoi_stats|dynpoi_status|dynpoi_status_id_seq|dynpoi_update|dynpoi_update_last" osmose_frontend > schema.sql
