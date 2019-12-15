CREATE OR REPLACE FUNCTION uuid_to_bigint(uuid uuid) RETURNS bigint AS $$
  SELECT ('x0' || replace(right(uuid::varchar, 16), '-', ''))::bit(64)::bigint
$$ LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;

ALTER TABLE marker
  DROP COLUMN id,
  DROP COLUMN subclass
;

DROP INDEX idx_marker_uuid;
ALTER TABLE marker ADD PRIMARY KEY (uuid);
CREATE INDEX idx_marker_id ON marker((uuid_to_bigint(marker.uuid)));

ALTER TABLE dynpoi_status
  DROP COLUMN id,
  DROP COLUMN subclass
;
CREATE INDEX idx_dynpoi_status_id ON dynpoi_status((uuid_to_bigint(dynpoi_status.uuid)));

DROP SEQUENCE dynpoi_status_id_seq;
