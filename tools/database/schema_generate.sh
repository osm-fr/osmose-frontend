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

  (d.objid IS NULL OR proname = 'marker_elem_ids')
ORDER BY
  p.proname
" > schema.sql

pg_dump --no-tablespaces -s -O -x -t "backends|markers|categories|markers_counts|class|items|sources|sources_password|stats|markers_status|updates|updates_last" -h "$DB_HOST" -U osmose osmose_frontend >> schema.sql
