DROP INDEX idx_marker_source_class_subclass_lat_lon_elems;
DROP INDEX idx_marker_z_order_curve;

CREATE INDEX idx_marker_source_class_z_order_curve ON marker USING btree (source, class, lonlat2z_order_curve(lon, lat) WHERE lat > -90;
CREATE INDEX idx_marker_z_order_curve_item ON marker USING btree (lonlat2z_order_curve(lon, lat), item) WHERE lat > -90;
