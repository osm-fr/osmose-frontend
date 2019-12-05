ALTER TABLE marker DROP COLUMN elems;

ALTER TABLE marker ADD COLUMN elems jsonb[];
ALTER TABLE marker ADD COLUMN fixes jsonb[];

CREATE TEMP TABLE elems AS
SELECT
  marker_id,
  array_agg(elem) AS elems
FROM (
  SELECT
    marker_id,
    elem_index,
    json_strip_nulls(json_build_object(
      'type', data_type,
      'id', id,
      'tags', NULLIF(tags, '{}'::jsonb),
      'username', username
    )) AS elem
  FROM
    marker_elem
  ORDER BY
    marker_id,
    elem_index
) AS t
GROUP BY
  marker_id
;
ALTER TABLE elems ADD PRIMARY KEY (marker_id);

CREATE TEMP TABLE fixes AS
SELECT
  marker_id,
  array_agg(fix_elems) AS fixes
FROM (
  SELECT
    marker_id,
    jsonb_agg(fix) AS fix_elems
  FROM (
    SELECT
      marker_id,
      diff_index,
      json_strip_nulls(json_build_object(
        'type', CASE WHEN elem_id != 0 THEN elem_data_type ELSE NULL END,
        'id', NULLIF(elem_id, 0),
        'create', NULLIF(tags_create, '{}'::jsonb),
        'modify', NULLIF(tags_modify, '{}'::jsonb),
        'delete', NULLIF(tags_delete, ARRAY[]::text[])
      )) AS fix
    FROM
      marker_fix
    ORDER BY
      marker_id,
      diff_index
    ) AS t
  GROUP BY
    marker_id,
    diff_index
) AS t
GROUP BY
  marker_id
;
ALTER TABLE fixes ADD PRIMARY KEY (marker_id);

UPDATE marker SET
  elems = (SELECT elems FROM elems WHERE marker_id = marker.id),
  fixes = (SELECT fixes FROM fixes WHERE marker_id = marker.id)
;

CREATE OR REPLACE FUNCTION marker_elem_ids(elems jsonb[]) RETURNS bigint[] AS $$
  SELECT
    array_agg((elem->>'id')::bigint)
  FROM (
    SELECT
      unnest(elems)
  ) AS t(elem)
$$ LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;

CREATE INDEX idx_marker_elem_ids ON marker USING GIN(marker_elem_ids(elems));

CREATE OR REPLACE FUNCTION marker_usernames(elems jsonb[]) RETURNS text[] AS $$
  SELECT
    array_agg(elem->>'username')
  FROM (
    SELECT
      unnest(elems)
  ) AS t(elem)
$$ LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;

CREATE INDEX idx_marker_usernames ON marker USING GIN(marker_usernames(elems));

DROP TABLE marker_elem;
DROP TABLE marker_fix;

ALTER TABLE dynpoi_status ADD COLUMN elems_ jsonb[];

UPDATE dynpoi_status SET elems_ = (
  SELECT
    array_agg(json_build_object(
      'type', upper(a[1]),
      'id', a[2]::bigint
    ))
  FROM (SELECT (regexp_matches(regexp_split_to_table(elems, '_'), '([nwr])[a-z]+([0-9]+)'))) AS t(a)
)
;

ALTER TABLE dynpoi_status DROP COLUMN elems;
ALTER TABLE dynpoi_status RENAME COLUMN elems_ TO elems;
