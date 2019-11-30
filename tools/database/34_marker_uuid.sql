ALTER TABLE marker ADD COLUMN uuid uuid;
UPDATE marker SET uuid = ('{' || encode(substring(digest(
  source || '/' ||
  class || '/' ||
  subclass || '/' ||
  (SELECT string_agg(s, '_') from (SELECT * FROM regexp_split_to_table(elems, '_') AS t(s) ORDER BY s) AS d),
  'sha256') FROM 1 FOR 16), 'hex') || '}')::uuid;
ALTER TABLE marker ALTER COLUMN uuid SET NOT NULL;

ALTER TABLE dynpoi_status ADD COLUMN uuid uuid;
UPDATE dynpoi_status SET uuid = ('{' || encode(substring(digest(
  source || '/' ||
  class || '/' ||
  subclass || '/' ||
  (SELECT string_agg(s, '_') from (SELECT * FROM regexp_split_to_table(elems, '_') AS t(s) ORDER BY s) AS d),
  'sha256') FROM 1 FOR 16), 'hex') || '}')::uuid;
ALTER TABLE dynpoi_status ALTER COLUMN uuid SET NOT NULL;
