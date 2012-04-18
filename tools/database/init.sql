DROP TABLE IF EXISTS marker CASCADE;
DROP TABLE IF EXISTS marker_elem CASCADE;

CREATE TABLE marker (
  id bigserial PRIMARY KEY,
  source integer,
  class integer,
  subclass integer,
  lat integer,
  lon integer,
  elems text,
  item integer,
  subtitle hstore
);

CREATE TABLE marker_elem (
  marker_id bigint references marker(id) ON DELETE CASCADE,
  elem_index integer,
  data_type char,
  id bigint,
  tags hstore,
  username text,
  PRIMARY KEY (marker_id, elem_index)
);


CREATE INDEX idx_marker_lat ON marker USING btree(lat);
CREATE INDEX idx_marker_lon ON marker USING btree(lon);
CREATE INDEX idx_marker_item ON marker USING btree(item);
CREATE INDEX idx_marker_source_class ON marker USING btree(source, class);
CREATE INDEX idx_marker_source_class_subclass_lat_lon_elems ON marker USING btree(source, class, subclass, lat, lon, elems);


CREATE INDEX idx_marker_elem_data_type_id ON marker_elem USING btree(data_type, id);
CREATE INDEX idx_marker_elem_username ON marker_elem USING btree(username);
