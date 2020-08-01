CREATE OR REPLACE FUNCTION public.lon2tile(lon double precision, zoom integer)
 RETURNS integer
 LANGUAGE sql
 IMMUTABLE
AS $function$
  SELECT FLOOR( (lon + 180) / 360 * (1 << zoom) )::integer;
$function$;

CREATE OR REPLACE FUNCTION public.lat2tile(lat double precision, zoom integer)
 RETURNS integer
 LANGUAGE sql
 IMMUTABLE
AS $function$
  SELECT floor( (1.0 - ln(tan(radians(lat)) + 1.0 / cos(radians(lat))) / pi()) / 2.0 * (1 << zoom) )::integer;
$function$;

CREATE OR REPLACE FUNCTION public.z_order_curve(xx integer, yy integer)
 RETURNS bigint
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
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
$function$;

CREATE OR REPLACE FUNCTION public.lonlat2z_order_curve(lon double precision, lat double precision)
 RETURNS bigint
 LANGUAGE sql
 IMMUTABLE
AS $function$
  SELECT public.z_order_curve(public.lon2tile(lon, 18), public.lat2tile(lat, 18));
$function$;

CREATE OR REPLACE FUNCTION public.zoc18min(zoc bigint, z integer)
 RETURNS bigint
 LANGUAGE sql
 IMMUTABLE
AS $function$
  SELECT zoc << (2 * (18 - z));
$function$;

CREATE OR REPLACE FUNCTION public.zoc18max(zoc bigint, z integer)
 RETURNS bigint
 LANGUAGE sql
 IMMUTABLE
AS $function$
  SELECT public.zoc18min(zoc, z) + power(2, 2 * (18 - z))::bigint - 1;
$function$;

CREATE OR REPLACE FUNCTION public.marker_elem_ids(elems jsonb[])
 RETURNS bigint[]
 LANGUAGE sql
 IMMUTABLE STRICT
AS $function$
  SELECT
    array_agg((elem->>'id')::bigint)
  FROM (
    SELECT
      unnest(elems)
  ) AS t(elem)
$function$;

CREATE OR REPLACE FUNCTION public.marker_usernames(elems jsonb[])
 RETURNS text[]
 LANGUAGE sql
 IMMUTABLE STRICT
AS $function$
  SELECT
    array_agg(elem->>'username')
  FROM (
    SELECT
      unnest(elems)
  ) AS t(elem)
$function$;

CREATE OR REPLACE FUNCTION public.uuid_to_bigint(uuid uuid)
 RETURNS bigint
 LANGUAGE sql
 IMMUTABLE STRICT
AS $function$
  SELECT ('x0' || replace(right(uuid::varchar, 16), '-', ''))::bit(64)::bigint
$function$;

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.8
-- Dumped by pg_dump version 11.7 (Debian 11.7-0+deb10u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_with_oids = false;

--
-- Name: backends; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backends (
    ip character varying(128) NOT NULL,
    hostname character varying(256) NOT NULL
);


--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    menu jsonb
);


--
-- Name: class; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.class (
    item integer NOT NULL,
    class integer NOT NULL,
    title jsonb,
    level integer,
    "timestamp" timestamp without time zone,
    tags character varying(255)[],
    detail jsonb,
    fix jsonb,
    trap jsonb,
    example jsonb,
    source text,
    resource text
);


--
-- Name: items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.items (
    item integer NOT NULL,
    categorie_id integer NOT NULL,
    marker_color character varying(16),
    marker_flag character varying(16),
    menu jsonb,
    levels integer[],
    number integer[],
    tags character varying[]
);


--
-- Name: markers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.markers (
    source_id integer,
    class integer,
    lat numeric(9,7),
    lon numeric(10,7),
    item integer,
    subtitle jsonb,
    uuid uuid NOT NULL,
    elems jsonb[],
    fixes jsonb[]
)
WITH (autovacuum_enabled='true', toast.autovacuum_enabled='true');


--
-- Name: markers_counts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.markers_counts (
    source_id integer NOT NULL,
    class integer NOT NULL,
    item integer,
    count integer
);


--
-- Name: markers_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.markers_status (
    source_id integer NOT NULL,
    class integer NOT NULL,
    date timestamp with time zone,
    status character varying(128),
    lat numeric(9,7) NOT NULL,
    lon numeric(10,7) NOT NULL,
    subtitle jsonb,
    uuid uuid NOT NULL,
    elems jsonb[],
    item integer NOT NULL
);


--
-- Name: sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sources (
    id integer NOT NULL,
    country character varying(256),
    analyser character varying(256)
);


--
-- Name: sources_password; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sources_password (
    source_id integer NOT NULL,
    password character varying(128) NOT NULL
);


--
-- Name: stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stats (
    source_id integer,
    class integer,
    count integer,
    timestamp_range tsrange
);


--
-- Name: updates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.updates (
    source_id integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    remote_url character varying(2048),
    remote_ip character varying(128),
    version text,
    analyser_version text
);


--
-- Name: updates_last; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.updates_last (
    source_id integer NOT NULL,
    "timestamp" timestamp with time zone,
    version text,
    remote_ip character varying(128) DEFAULT NULL::character varying,
    analyser_version text
);


--
-- Name: backends backend_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backends
    ADD CONSTRAINT backend_pkey PRIMARY KEY (ip, hostname);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);

ALTER TABLE public.categories CLUSTER ON categories_pkey;


--
-- Name: class class_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class
    ADD CONSTRAINT class_pkey PRIMARY KEY (item, class);


--
-- Name: items items_marker_color_flag; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_marker_color_flag UNIQUE (marker_color, marker_flag);


--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (item);

ALTER TABLE public.items CLUSTER ON items_pkey;


--
-- Name: markers_counts markers_counts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.markers_counts
    ADD CONSTRAINT markers_counts_pkey PRIMARY KEY (source_id, class);


--
-- Name: markers markers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.markers
    ADD CONSTRAINT markers_pkey PRIMARY KEY (uuid);


--
-- Name: markers_status markers_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.markers_status
    ADD CONSTRAINT markers_status_pkey PRIMARY KEY (uuid);


--
-- Name: sources_password sources_password_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sources_password
    ADD CONSTRAINT sources_password_pkey PRIMARY KEY (source_id, password);


--
-- Name: sources sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sources
    ADD CONSTRAINT sources_pkey PRIMARY KEY (id);


--
-- Name: updates_last updates_last_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.updates_last
    ADD CONSTRAINT updates_last_pkey PRIMARY KEY (source_id);

ALTER TABLE public.updates_last CLUSTER ON updates_last_pkey;


--
-- Name: updates updates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.updates
    ADD CONSTRAINT updates_pkey PRIMARY KEY (source_id, "timestamp");

ALTER TABLE public.updates CLUSTER ON updates_pkey;


--
-- Name: idx_dynpoi_class_class; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dynpoi_class_class ON public.markers_counts USING btree (class);

ALTER TABLE public.markers_counts CLUSTER ON idx_dynpoi_class_class;


--
-- Name: idx_dynpoi_class_item; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dynpoi_class_item ON public.markers_counts USING btree (item);


--
-- Name: idx_dynpoi_class_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dynpoi_class_source ON public.markers_counts USING btree (source_id);


--
-- Name: idx_marker_elem_ids; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_elem_ids ON public.markers USING gin (public.marker_elem_ids(elems));


--
-- Name: idx_marker_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_id ON public.markers USING btree (public.uuid_to_bigint(uuid));


--
-- Name: idx_marker_item; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_item ON public.markers USING btree (item);


--
-- Name: idx_marker_item_lat_lon; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_item_lat_lon ON public.markers USING btree (item, lat, lon);


--
-- Name: idx_marker_source_class; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_source_class ON public.markers USING btree (source_id, class);


--
-- Name: idx_marker_source_class_z_order_curve; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_source_class_z_order_curve ON public.markers USING btree (source_id, class, public.lonlat2z_order_curve((lon)::double precision, (lat)::double precision)) WHERE (lat > ('-90'::integer)::numeric);


--
-- Name: idx_marker_usernames; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_usernames ON public.markers USING gin (public.marker_usernames(elems));


--
-- Name: idx_marker_z_order_curve_item; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_z_order_curve_item ON public.markers USING btree (public.lonlat2z_order_curve((lon)::double precision, (lat)::double precision), item) WHERE (lat > ('-90'::integer)::numeric);


--
-- Name: idx_markers_status_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_markers_status_id ON public.markers_status USING btree (public.uuid_to_bigint(uuid));


--
-- Name: idx_markers_status_source_id_class; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_markers_status_source_id_class ON public.markers_status USING btree (source_id, class);


--
-- Name: idx_stats; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_stats ON public.stats USING btree (source_id, class);


--
-- Name: sources_country_analyser; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX sources_country_analyser ON public.sources USING btree (country, analyser);


--
-- Name: markers_status dynpoi_status_source_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.markers_status
    ADD CONSTRAINT dynpoi_status_source_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id);


--
-- Name: items item_categorie_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT item_categorie_fkey FOREIGN KEY (categorie_id) REFERENCES public.categories(id);


--
-- Name: markers_counts markers_counts_item_class_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.markers_counts
    ADD CONSTRAINT markers_counts_item_class_fkey FOREIGN KEY (item, class) REFERENCES public.class(item, class);


--
-- Name: markers_counts markers_counts_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.markers_counts
    ADD CONSTRAINT markers_counts_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id);


--
-- Name: markers markers_item_class_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.markers
    ADD CONSTRAINT markers_item_class_fkey FOREIGN KEY (item, class) REFERENCES public.class(item, class);


--
-- Name: markers markers_sources_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.markers
    ADD CONSTRAINT markers_sources_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id);


--
-- Name: markers_status markers_status_item_class_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.markers_status
    ADD CONSTRAINT markers_status_item_class_fkey FOREIGN KEY (item, class) REFERENCES public.class(item, class);


--
-- Name: sources_password sources_password_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sources_password
    ADD CONSTRAINT sources_password_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id);


--
-- Name: stats stats_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stats
    ADD CONSTRAINT stats_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id);


--
-- Name: updates_last updates_last_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.updates_last
    ADD CONSTRAINT updates_last_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id);


--
-- Name: updates updates_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.updates
    ADD CONSTRAINT updates_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id);


--
-- PostgreSQL database dump complete
--

