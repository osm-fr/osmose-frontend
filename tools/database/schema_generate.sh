#! /bin/sh

psql -h "$DB_HOST" -U osmose osmose_frontend -A --tuples-only -c "
SELECT
  left(pg_get_functiondef(p.oid), -1) || E';\n'
FROM
  pg_proc p
  JOIN pg_namespace n ON
    n.oid = p.pronamespace
  LEFT JOIN pg_depend d ON
    d.objid = p.oid AND
    d.deptype = 'e'
WHERE
  nspname = 'public' AND
  NOT p.proisagg AND
  d.objid IS NULL
ORDER BY
  CASE p.proname
    WHEN 'lon2tile' THEN '1'
    WHEN 'lat2tile' THEN '2'
    WHEN 'z_order_curve' THEN '3'
    WHEN 'lonlat2z_order_curve' THEN '4'
    WHEN 'zoc18min' THEN '5'
    WHEN 'zoc18max' THEN '6'
    ELSE p.proname
  END
" > schema.sql

pg_dump --no-tablespaces -s -O -x -t "backend|marker*|dynpoi_categ|dynpoi_class|class|dynpoi_item|source|source_password|dynpoi_stats|dynpoi_status|dynpoi_status_id_seq|dynpoi_update|dynpoi_update_last" -h "$DB_HOST" -U osmose osmose_frontend >> schema.sql
