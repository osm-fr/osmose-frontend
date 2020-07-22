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

  p.prokind = 'f' AND
-- Before Postgres 11:
--  NOT p.proisagg AND

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

pg_dump --no-tablespaces -s -O -x -t "backend|marker*|categories|dynpoi_class|class|items|source|source_password|stats|dynpoi_status|dynpoi_status_id_seq|updates|updates_last" -h "$DB_HOST" -U osmose osmose_frontend >> schema.sql
