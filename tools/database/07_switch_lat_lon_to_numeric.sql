DROP INDEX idx_marker_lat;
DROP INDEX idx_marker_lon;
DROP INDEX marker_geom;

ALTER TABLE marker ALTER COLUMN lon TYPE numeric(10,7) USING lon / 1000000.;
ALTER TABLE marker ALTER COLUMN lat TYPE numeric(9,7)  USING lat / 1000000.;
ALTER TABLE dynpoi_status ALTER COLUMN lon TYPE numeric(10,7) USING lon / 1000000.;
ALTER TABLE dynpoi_status ALTER COLUMN lat TYPE numeric(9,7)  USING lat / 1000000.;

CREATE INDEX idx_marker_lat ON marker USING btree(lat);
CREATE INDEX idx_marker_lon ON marker USING btree(lon);
CREATE INDEX marker_geom ON marker USING gist(point(lat, lon));
