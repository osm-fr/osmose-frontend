DROP INDEX idx_marker_lat_lon;


CREATE OR REPLACE FUNCTION public.lon2tile(lon double precision, zoom integer) RETURNS integer AS $$
  SELECT FLOOR( (lon + 180) / 360 * (1 << zoom) )::integer;
$$ LANGUAGE SQL IMMUTABLE;

CREATE OR REPLACE FUNCTION public.lat2tile(lat double precision, zoom integer) RETURNS integer AS $$
  SELECT floor( (1.0 - ln(tan(radians(lat)) + 1.0 / cos(radians(lat))) / pi()) / 2.0 * (1 << zoom) )::integer;
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION public.z_order_curve(xx integer, yy integer) RETURNS bigint AS $$
DECLARE
  B bigint[] := ARRAY[x'5555555555555555'::bigint, x'3333333333333333'::bigint, x'0F0F0F0F0F0F0F0F'::bigint, x'00FF00FF00FF00FF'::bigint, x'0000FFFF0000FFFF'::bigint];
  S integer[] := ARRAY[1, 2, 4, 8, 16];
  x bigint := xx;
  y bigint := yy;
  z bigint;
BEGIN
  x := (x | (x << S[5])) & B[5];
  x := (x | (x << S[4])) & B[4];
  x := (x | (x << S[3])) & B[3];
  x := (x | (x << S[2])) & B[2];
  x := (x | (x << S[1])) & B[1];
  y := (y | (y << S[5])) & B[5];
  y := (y | (y << S[4])) & B[4];
  y := (y | (y << S[3])) & B[3];
  y := (y | (y << S[2])) & B[2];
  y := (y | (y << S[1])) & B[1];
  z := x | (y << 1);
  return z::bigint;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE OR REPLACE FUNCTION public.lonlat2z_order_curve(lon double precision, lat double precision) RETURNS bigint AS $$
  SELECT public.z_order_curve(public.lon2tile(lon, 18), public.lat2tile(lat, 18));
$$ LANGUAGE sql IMMUTABLE;

CREATE INDEX idx_marker_z_order_curve ON marker((public.lonlat2z_order_curve(lon, lat))) WHERE lat > -90;


CREATE OR REPLACE FUNCTION public.zoc18min(zoc bigint, z integer) RETURNS bigint AS $$
  SELECT zoc << (2 * (18 - z));
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION public.zoc18max(zoc bigint, z integer) RETURNS bigint AS $$
  SELECT public.zoc18min(zoc, z) + power(2, 2 * (18 - z))::bigint - 1;
$$ LANGUAGE sql IMMUTABLE;
