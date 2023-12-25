CREATE INDEX idx_marker_item_source_class_point ON public.markers USING gist (item, source_id, class, point((lon)::double precision, (lat)::double precision));
CREATE INDEX idx_marker_point_item_2 ON public.markers USING gist (item, point((lon)::double precision, (lat)::double precision));
CREATE INDEX idx_marker_point_item_4 ON public.markers USING gist (point((lon)::double precision, (lat)::double precision));
CREATE INDEX idx_marker_source_class_box_point_2 ON public.markers USING gist (source_id, class, point((lon)::double precision, (lat)::double precision));
DROP INDEX IF EXISTS idx_marker_item;
DROP INDEX IF EXISTS idx_marker_item_lat_lon;
