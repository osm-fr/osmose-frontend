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
    array_agg((elem->'id')::bigint)
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
    array_agg((elem->'username')::text)
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

-- Dumped from database version 11.6
-- Dumped by pg_dump version 11.5 (Debian 11.5-1+deb10u1)

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
-- Name: backend; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend (
    ip character varying(128) NOT NULL,
    hostname character varying(256) NOT NULL
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
    tags character varying(255)[]
);


--
-- Name: dynpoi_categ; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dynpoi_categ (
    categ integer NOT NULL,
    menu jsonb
);


--
-- Name: dynpoi_class; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dynpoi_class (
    source integer NOT NULL,
    class integer NOT NULL,
    item integer,
    "timestamp" timestamp without time zone,
    count integer
);


--
-- Name: dynpoi_item; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dynpoi_item (
    item integer NOT NULL,
    categ integer,
    marker_color character varying(16),
    marker_flag character varying(16),
    menu jsonb,
    levels integer[],
    number integer[],
    tags character varying[]
);


--
-- Name: dynpoi_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dynpoi_stats (
    source integer NOT NULL,
    class integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    count integer NOT NULL
);


--
-- Name: dynpoi_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dynpoi_status (
    source integer NOT NULL,
    class integer NOT NULL,
    date timestamp with time zone,
    status character varying(128),
    lat numeric(9,7) NOT NULL,
    lon numeric(10,7) NOT NULL,
    subtitle jsonb,
    uuid uuid NOT NULL,
    elems jsonb[]
);


--
-- Name: dynpoi_update; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dynpoi_update (
    source integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    remote_url character varying(2048),
    remote_ip character varying(128),
    version text,
    analyser_version text
);


--
-- Name: dynpoi_update_last; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dynpoi_update_last (
    source integer NOT NULL,
    "timestamp" timestamp with time zone,
    version text,
    remote_ip character varying(128) DEFAULT NULL::character varying,
    analyser_version text
);


--
-- Name: marker; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.marker (
    source integer,
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
-- Name: source; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.source (
    id integer NOT NULL,
    country character varying(256),
    analyser character varying(256)
);


--
-- Name: source_password; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.source_password (
    source_id integer NOT NULL,
    password character varying(128) NOT NULL
);


--
-- Name: backend backend_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend
    ADD CONSTRAINT backend_pkey PRIMARY KEY (ip, hostname);


--
-- Name: class class_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class
    ADD CONSTRAINT class_pkey PRIMARY KEY (item, class);


--
-- Name: dynpoi_categ dynpoi_categ_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_categ
    ADD CONSTRAINT dynpoi_categ_pkey PRIMARY KEY (categ);

ALTER TABLE public.dynpoi_categ CLUSTER ON dynpoi_categ_pkey;


--
-- Name: dynpoi_class dynpoi_class_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_class
    ADD CONSTRAINT dynpoi_class_pkey PRIMARY KEY (source, class);


--
-- Name: dynpoi_item dynpoi_item_marker; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_item
    ADD CONSTRAINT dynpoi_item_marker UNIQUE (marker_color, marker_flag);


--
-- Name: dynpoi_item dynpoi_item_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_item
    ADD CONSTRAINT dynpoi_item_pkey PRIMARY KEY (item);

ALTER TABLE public.dynpoi_item CLUSTER ON dynpoi_item_pkey;


--
-- Name: dynpoi_stats dynpoi_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_stats
    ADD CONSTRAINT dynpoi_stats_pkey PRIMARY KEY (source, class, "timestamp");

ALTER TABLE public.dynpoi_stats CLUSTER ON dynpoi_stats_pkey;


--
-- Name: dynpoi_status dynpoi_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_status
    ADD CONSTRAINT dynpoi_status_pkey PRIMARY KEY (source, class, uuid);


--
-- Name: dynpoi_update_last dynpoi_update_last_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_update_last
    ADD CONSTRAINT dynpoi_update_last_pkey PRIMARY KEY (source);

ALTER TABLE public.dynpoi_update_last CLUSTER ON dynpoi_update_last_pkey;


--
-- Name: dynpoi_update dynpoi_update_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_update
    ADD CONSTRAINT dynpoi_update_pkey PRIMARY KEY (source, "timestamp");

ALTER TABLE public.dynpoi_update CLUSTER ON dynpoi_update_pkey;


--
-- Name: marker marker_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marker
    ADD CONSTRAINT marker_pkey PRIMARY KEY (uuid);


--
-- Name: source_password source_password_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_password
    ADD CONSTRAINT source_password_pkey PRIMARY KEY (source_id, password);


--
-- Name: source source_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source
    ADD CONSTRAINT source_pkey PRIMARY KEY (id);


--
-- Name: idx_dynpoi_class_class; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dynpoi_class_class ON public.dynpoi_class USING btree (class);

ALTER TABLE public.dynpoi_class CLUSTER ON idx_dynpoi_class_class;


--
-- Name: idx_dynpoi_class_item; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dynpoi_class_item ON public.dynpoi_class USING btree (item);


--
-- Name: idx_dynpoi_class_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dynpoi_class_source ON public.dynpoi_class USING btree (source);


--
-- Name: idx_dynpoi_status_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dynpoi_status_id ON public.dynpoi_status USING btree ((((('x0'::text || replace("right"(((uuid)::character varying)::text, 16), '-'::text, ''::text)))::bit(64))::bigint));


--
-- Name: idx_marker_elem_ids; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_elem_ids ON public.marker USING gin (public.marker_elem_ids(elems));


--
-- Name: idx_marker_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_id ON public.marker USING btree ((((('x0'::text || replace("right"(((uuid)::character varying)::text, 16), '-'::text, ''::text)))::bit(64))::bigint));


--
-- Name: idx_marker_item; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_item ON public.marker USING btree (item);


--
-- Name: idx_marker_source_class; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_source_class ON public.marker USING btree (source, class);


--
-- Name: idx_marker_source_class_z_order_curve; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_source_class_z_order_curve ON public.marker USING btree (source, class, public.lonlat2z_order_curve((lon)::double precision, (lat)::double precision)) WHERE (lat > ('-90'::integer)::numeric);


--
-- Name: idx_marker_usernames; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_usernames ON public.marker USING gin (public.marker_usernames(elems));


--
-- Name: idx_marker_z_order_curve_item; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_z_order_curve_item ON public.marker USING btree (public.lonlat2z_order_curve((lon)::double precision, (lat)::double precision), item) WHERE (lat > ('-90'::integer)::numeric);


--
-- Name: source_country_analyser; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX source_country_analyser ON public.source USING btree (country, analyser);


--
-- Name: dynpoi_class class_item_class_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_class
    ADD CONSTRAINT class_item_class_fkey FOREIGN KEY (item, class) REFERENCES public.class(item, class);


--
-- Name: dynpoi_class dynpoi_class_source_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_class
    ADD CONSTRAINT dynpoi_class_source_fkey FOREIGN KEY (source) REFERENCES public.source(id);


--
-- Name: dynpoi_status dynpoi_status_source_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_status
    ADD CONSTRAINT dynpoi_status_source_fkey FOREIGN KEY (source) REFERENCES public.source(id);


--
-- Name: marker marker_class_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marker
    ADD CONSTRAINT marker_class_fkey FOREIGN KEY (source, class) REFERENCES public.dynpoi_class(source, class);


--
-- Name: marker marker_source_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marker
    ADD CONSTRAINT marker_source_fkey FOREIGN KEY (source) REFERENCES public.source(id);


--
-- Name: source_password source_password_source_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source_password
    ADD CONSTRAINT source_password_source_fkey FOREIGN KEY (source_id) REFERENCES public.source(id);


--
-- PostgreSQL database dump complete
--

