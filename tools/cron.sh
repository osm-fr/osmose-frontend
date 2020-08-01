#! /bin/bash

set -e

DATABASE=osmose_frontend
DIR_DUMP="/data/work/$(whoami)/"


# Update various tables in database

psql -d $DATABASE -c "
DELETE FROM markers_status
WHERE date < now()-interval '7 day' AND status = 'done';
"

psql -d $DATABASE -c "
CREATE TEMP TABLE stats_update AS
SELECT
  c.source_id,
  c.class,
  now()::timestamp AS timestamp,
  c.count
FROM (
  SELECT
    markers_counts.source_id,
    markers_counts.class,
    count(markers.source_id) AS count
  FROM markers_counts
    LEFT JOIN markers ON
      markers_counts.source_id = markers.source_id AND
      markers_counts.class = markers.class
  GROUP BY
    markers_counts.source_id,
    markers_counts.class
  ) AS c
    LEFT JOIN stats ON
      stats.source_id = c.source_id AND
      stats.class = c.class
WHERE
  stats.count IS NULL OR
  (
    upper(stats.timestamp_range) IS NULL AND
    stats.count != c.count
  )
;

-- Close last range
UPDATE
  stats
SET
  timestamp_range = tsrange(lower(timestamp_range), stats_update.timestamp)
FROM
  stats_update
WHERE
  stats_update.source_id = stats.source_id AND
  stats_update.class = stats.class AND
  upper(stats.timestamp_range) IS NULL
;

-- Open new range
INSERT INTO stats (
  SELECT
    source_id,
    class,
    count,
    tsrange(timestamp, NULL)
  FROM
    stats_update
);
"

psql -d $DATABASE -c "
UPDATE items SET levels = (
  SELECT array_agg(level)
  FROM (
    SELECT level
    FROM class
    WHERE item = items.item
    GROUP BY level
    ORDER BY level
  ) AS a
);
"

psql -d $DATABASE -c "
UPDATE items SET number = (
  SELECT array_agg(n)
  FROM (
    SELECT sum(CASE WHEN markers.item IS NOT NULL THEN 1 ELSE 0 END) AS n
    FROM class
      LEFT JOIN markers ON markers.item = items.item
    WHERE class.item = items.item
    GROUP BY level
    ORDER BY level
  ) AS a
);
"

psql -d $DATABASE -c "
UPDATE items SET tags = (
  SELECT array_agg(tag)
  FROM (
    SELECT tag
    FROM (
      SELECT unnest(tags) AS tag
      FROM class
      WHERE item = items.item
      ) AS a
    WHERE tag != ''
    GROUP BY tag
    ORDER BY tag
  ) AS a
);
"

mkdir -p "$DIR_DUMP/tmp"
mkdir -p "$DIR_DUMP/export"


# Dump of errors - commented, because it takes a long time on a big database

#pg_dump -t categories -t markers_counts -t items -t updates_last -t markers -t sources $DATABASE \
#  | bzip2 > "$DIR_DUMP/tmp/osmose-planet-latest.sql.bz2.tmp"
#mv "$DIR_DUMP/tmp/osmose-planet-latest.sql.bz2.tmp" "$DIR_DUMP/export/osmose-planet-latest.sql.bz2"
#
#psql $DATABASE -c "COPY (SELECT source.country,
#             source.analyser,
#             markers.lat,
#             markers.lon,
#             markers.elems,
#             markers.class,
#             markers.subclass,
#             markers.item
#      FROM markers
#      LEFT JOIN sources ON sources.id = markers.source_id)
#TO STDOUT WITH CSV HEADER;" | bzip2 > "$DIR_DUMP/tmp/osmose-planet-latest.csv.bz2"
#mv "$DIR_DUMP/tmp/osmose-planet-latest.csv.bz2" "$DIR_DUMP/export/osmose-planet-latest.csv.bz2"


# Dump menu items

pg_dump --data-only -t categories -t items $DATABASE \
  | bzip2 > "$DIR_DUMP/tmp/osmose-menu.sql.bz2.tmp"
mv "$DIR_DUMP/tmp/osmose-menu.sql.bz2.tmp" "$DIR_DUMP/export/osmose-menu.sql.bz2"
