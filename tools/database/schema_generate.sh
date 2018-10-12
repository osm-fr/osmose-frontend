#! /bin/sh

psql osmose_frontend -A -c "
SELECT
  pg_get_functiondef(p.oid)
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
  p.proname
" > schema.sql

pg_dump --no-tablespaces -s -O -x -t "marker*|dynpoi_categ|dynpoi_class|class|dynpoi_item|source|source_password|dynpoi_stats|dynpoi_status|dynpoi_status_id_seq|dynpoi_update|dynpoi_update_last" osmose_frontend >> schema.sql
