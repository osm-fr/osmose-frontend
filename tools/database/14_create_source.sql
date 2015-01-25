DROP TABLE IF EXISTS source CASCADE;
DROP TABLE IF EXISTS source_password CASCADE;

CREATE TABLE source (
  id integer NOT NULL PRIMARY KEY,
  country character varying(256),
  analyser character varying(256)
);

CREATE TABLE source_password (
  source_id integer NOT NULL PRIMARY KEY,
  password character varying(128)
);

CREATE UNIQUE INDEX source_password_password ON source_password USING btree (password);
CREATE UNIQUE INDEX source_country_analyser ON source USING btree (country, analyser);

INSERT INTO source (id, country, analyser)
  SELECT source, substring(comment from '-([^-]*)$'), substring(comment from '^(.*)-[^-]*$')
  FROM dynpoi_source;

INSERT INTO source_password (source_id, password)
  SELECT source, update FROM dynpoi_source;


ALTER TABLE dynpoi_class DROP CONSTRAINT IF EXISTS dynpoi_class_source_fkey;
ALTER TABLE dynpoi_status DROP CONSTRAINT IF EXISTS dynpoi_status_source_fkey;
ALTER TABLE marker DROP CONSTRAINT IF EXISTS marker_source_fkey;

ALTER TABLE dynpoi_class
  ADD CONSTRAINT dynpoi_class_source_fkey FOREIGN KEY (source) REFERENCES source(id);

ALTER TABLE dynpoi_status
 ADD CONSTRAINT dynpoi_status_source_fkey FOREIGN KEY (source) REFERENCES source(id);

ALTER TABLE marker
    ADD CONSTRAINT marker_source_fkey FOREIGN KEY (source) REFERENCES source(id);
