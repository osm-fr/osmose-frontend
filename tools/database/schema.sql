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

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.10
-- Dumped by pg_dump version 9.6.10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
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
    title public.hstore,
    level integer,
    "timestamp" timestamp without time zone,
    tags character varying(255)[]
);


--
-- Name: dynpoi_categ; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dynpoi_categ (
    categ integer NOT NULL,
    menu public.hstore
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
    menu public.hstore,
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
-- Name: dynpoi_status_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dynpoi_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dynpoi_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dynpoi_status (
    source integer NOT NULL,
    class integer NOT NULL,
    subclass integer NOT NULL,
    elems character varying(128) NOT NULL,
    date timestamp with time zone,
    status character varying(128),
    lat numeric(9,7) NOT NULL,
    lon numeric(10,7) NOT NULL,
    subtitle public.hstore,
    id bigint DEFAULT nextval('public.dynpoi_status_id_seq'::regclass)
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
    id bigint NOT NULL,
    source integer,
    class integer,
    subclass integer,
    lat numeric(9,7),
    lon numeric(10,7),
    elems text,
    item integer,
    subtitle public.hstore
)
WITH (autovacuum_enabled='true', toast.autovacuum_enabled='true');


--
-- Name: marker_elem; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.marker_elem (
    marker_id bigint NOT NULL,
    elem_index integer NOT NULL,
    data_type character(1),
    id bigint,
    tags public.hstore,
    username text
)
WITH (autovacuum_enabled='true', toast.autovacuum_enabled='true');


--
-- Name: marker_fix; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.marker_fix (
    marker_id bigint NOT NULL,
    diff_index integer NOT NULL,
    elem_data_type character(1) NOT NULL,
    elem_id bigint NOT NULL,
    tags_create public.hstore,
    tags_modify public.hstore,
    tags_delete text[]
);


--
-- Name: marker_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.marker_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: marker_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.marker_id_seq OWNED BY public.marker.id;


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
-- Name: marker id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marker ALTER COLUMN id SET DEFAULT nextval('public.marker_id_seq'::regclass);


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
-- Name: dynpoi_status dynpoi_status_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_status
    ADD CONSTRAINT dynpoi_status_id UNIQUE (id);


--
-- Name: dynpoi_status dynpoi_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dynpoi_status
    ADD CONSTRAINT dynpoi_status_pkey PRIMARY KEY (source, class, subclass, elems, lat, lon);


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
-- Name: marker_elem marker_elem_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marker_elem
    ADD CONSTRAINT marker_elem_pkey PRIMARY KEY (marker_id, elem_index);

ALTER TABLE public.marker_elem CLUSTER ON marker_elem_pkey;


--
-- Name: marker_fix marker_fix_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marker_fix
    ADD CONSTRAINT marker_fix_pkey PRIMARY KEY (marker_id, diff_index, elem_data_type, elem_id);

ALTER TABLE public.marker_fix CLUSTER ON marker_fix_pkey;


--
-- Name: marker marker_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marker
    ADD CONSTRAINT marker_pkey PRIMARY KEY (id);

ALTER TABLE public.marker CLUSTER ON marker_pkey;


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
-- Name: idx_marker_elem_username; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_elem_username ON public.marker_elem USING btree (username);


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
-- Name: marker_elem marker_elem_marker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marker_elem
    ADD CONSTRAINT marker_elem_marker_id_fkey FOREIGN KEY (marker_id) REFERENCES public.marker(id) ON DELETE CASCADE;


--
-- Name: marker_fix marker_fix_marker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marker_fix
    ADD CONSTRAINT marker_fix_marker_id_fkey FOREIGN KEY (marker_id) REFERENCES public.marker(id) ON DELETE CASCADE;


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

