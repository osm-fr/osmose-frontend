DROP FUNCTION lon2tile(lon double precision, zoom integer);
DROP FUNCTION lat2tile(lat double precision, zoom integer);
DROP FUNCTION z_order_curve(xx integer, yy integer);
DROP FUNCTION lonlat2z_order_curve(lon double precision, lat double precision);
DROP FUNCTION zoc18min(zoc bigint, z integer);
DROP FUNCTION zoc18max(zoc bigint, z integer);
DROP INDEX IF EXISTS idx_marker_source_class_z_order_curve;
DROP INDEX IF EXISTS idx_marker_z_order_curve_item;
