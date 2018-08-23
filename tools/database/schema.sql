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
-- Name: dynpoi_categ; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE dynpoi_categ (
    categ integer NOT NULL,
    menu hstore
);


--
-- Name: dynpoi_class; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE dynpoi_class (
    source integer NOT NULL,
    class integer NOT NULL,
    item integer,
    title hstore,
    level integer,
    "timestamp" timestamp without time zone,
    tags character varying(255)[],
    count integer
);


--
-- Name: dynpoi_item; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE dynpoi_item (
    item integer NOT NULL,
    categ integer,
    marker_color character varying(16),
    marker_flag character varying(16),
    menu hstore,
    levels integer[],
    number integer[],
    tags character varying[]
);


--
-- Name: dynpoi_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE dynpoi_stats (
    source integer NOT NULL,
    class integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    count integer NOT NULL
);


--
-- Name: dynpoi_status_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE dynpoi_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dynpoi_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE dynpoi_status (
    source integer NOT NULL,
    class integer NOT NULL,
    subclass integer NOT NULL,
    elems character varying(128) NOT NULL,
    date timestamp with time zone,
    status character varying(128),
    lat numeric(9,7) NOT NULL,
    lon numeric(10,7) NOT NULL,
    subtitle hstore,
    id bigint DEFAULT nextval('dynpoi_status_id_seq'::regclass)
);


--
-- Name: dynpoi_update; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE dynpoi_update (
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

CREATE TABLE dynpoi_update_last (
    source integer NOT NULL,
    "timestamp" timestamp with time zone,
    version text,
    remote_ip character varying(128) DEFAULT NULL::character varying,
    analyser_version text
);


--
-- Name: marker; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE marker (
    id bigint NOT NULL,
    source integer,
    class integer,
    subclass integer,
    lat numeric(9,7),
    lon numeric(10,7),
    elems text,
    item integer,
    subtitle hstore
)
WITH (autovacuum_enabled='true', toast.autovacuum_enabled='true');


--
-- Name: marker_elem; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE marker_elem (
    marker_id bigint NOT NULL,
    elem_index integer NOT NULL,
    data_type character(1),
    id bigint,
    tags hstore,
    username text
)
WITH (autovacuum_enabled='true', toast.autovacuum_enabled='true');


--
-- Name: marker_fix; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE marker_fix (
    marker_id bigint NOT NULL,
    diff_index integer NOT NULL,
    elem_data_type character(1) NOT NULL,
    elem_id bigint NOT NULL,
    tags_create hstore,
    tags_modify hstore,
    tags_delete text[]
);


--
-- Name: marker_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE marker_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: marker_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE marker_id_seq OWNED BY marker.id;


--
-- Name: source; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE source (
    id integer NOT NULL,
    country character varying(256),
    analyser character varying(256)
);


--
-- Name: source_password; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE source_password (
    source_id integer NOT NULL,
    password character varying(128) NOT NULL
);


--
-- Name: marker id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY marker ALTER COLUMN id SET DEFAULT nextval('marker_id_seq'::regclass);


--
-- Name: dynpoi_categ dynpoi_categ_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dynpoi_categ
    ADD CONSTRAINT dynpoi_categ_pkey PRIMARY KEY (categ);

ALTER TABLE dynpoi_categ CLUSTER ON dynpoi_categ_pkey;


--
-- Name: dynpoi_class dynpoi_class_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dynpoi_class
    ADD CONSTRAINT dynpoi_class_pkey PRIMARY KEY (source, class);


--
-- Name: dynpoi_item dynpoi_item_marker; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dynpoi_item
    ADD CONSTRAINT dynpoi_item_marker UNIQUE (marker_color, marker_flag);


--
-- Name: dynpoi_item dynpoi_item_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dynpoi_item
    ADD CONSTRAINT dynpoi_item_pkey PRIMARY KEY (item);

ALTER TABLE dynpoi_item CLUSTER ON dynpoi_item_pkey;


--
-- Name: dynpoi_stats dynpoi_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dynpoi_stats
    ADD CONSTRAINT dynpoi_stats_pkey PRIMARY KEY (source, class, "timestamp");

ALTER TABLE dynpoi_stats CLUSTER ON dynpoi_stats_pkey;


--
-- Name: dynpoi_status dynpoi_status_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dynpoi_status
    ADD CONSTRAINT dynpoi_status_id UNIQUE (id);


--
-- Name: dynpoi_status dynpoi_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dynpoi_status
    ADD CONSTRAINT dynpoi_status_pkey PRIMARY KEY (source, class, subclass, elems, lat, lon);


--
-- Name: dynpoi_update_last dynpoi_update_last_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dynpoi_update_last
    ADD CONSTRAINT dynpoi_update_last_pkey PRIMARY KEY (source);

ALTER TABLE dynpoi_update_last CLUSTER ON dynpoi_update_last_pkey;


--
-- Name: dynpoi_update dynpoi_update_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dynpoi_update
    ADD CONSTRAINT dynpoi_update_pkey PRIMARY KEY (source, "timestamp");

ALTER TABLE dynpoi_update CLUSTER ON dynpoi_update_pkey;


--
-- Name: marker_elem marker_elem_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY marker_elem
    ADD CONSTRAINT marker_elem_pkey PRIMARY KEY (marker_id, elem_index);

ALTER TABLE marker_elem CLUSTER ON marker_elem_pkey;


--
-- Name: marker_fix marker_fix_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY marker_fix
    ADD CONSTRAINT marker_fix_pkey PRIMARY KEY (marker_id, diff_index, elem_data_type, elem_id);

ALTER TABLE marker_fix CLUSTER ON marker_fix_pkey;


--
-- Name: marker marker_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY marker
    ADD CONSTRAINT marker_pkey PRIMARY KEY (id);

ALTER TABLE marker CLUSTER ON marker_pkey;


--
-- Name: source_password source_password_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY source_password
    ADD CONSTRAINT source_password_pkey PRIMARY KEY (source_id, password);


--
-- Name: source source_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY source
    ADD CONSTRAINT source_pkey PRIMARY KEY (id);


--
-- Name: idx_dynpoi_class_class; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dynpoi_class_class ON dynpoi_class USING btree (class);

ALTER TABLE dynpoi_class CLUSTER ON idx_dynpoi_class_class;


--
-- Name: idx_dynpoi_class_item; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dynpoi_class_item ON dynpoi_class USING btree (item);


--
-- Name: idx_dynpoi_class_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dynpoi_class_level ON dynpoi_class USING btree (level);


--
-- Name: idx_dynpoi_class_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dynpoi_class_source ON dynpoi_class USING btree (source);


--
-- Name: idx_marker_elem_username; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_elem_username ON marker_elem USING btree (username);


--
-- Name: idx_marker_item; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_item ON marker USING btree (item);


--
-- Name: idx_marker_lat_lon; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_lat_lon ON marker USING btree (lat, lon);


--
-- Name: idx_marker_source_class; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_source_class ON marker USING btree (source, class);


--
-- Name: idx_marker_source_class_subclass_lat_lon_elems; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_marker_source_class_subclass_lat_lon_elems ON marker USING btree (source, class, subclass, lat, lon, elems);


--
-- Name: source_country_analyser; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX source_country_analyser ON source USING btree (country, analyser);


--
-- Name: dynpoi_class dynpoi_class_source_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dynpoi_class
    ADD CONSTRAINT dynpoi_class_source_fkey FOREIGN KEY (source) REFERENCES source(id);


--
-- Name: dynpoi_status dynpoi_status_source_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dynpoi_status
    ADD CONSTRAINT dynpoi_status_source_fkey FOREIGN KEY (source) REFERENCES source(id);


--
-- Name: marker marker_class_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY marker
    ADD CONSTRAINT marker_class_fkey FOREIGN KEY (source, class) REFERENCES dynpoi_class(source, class);


--
-- Name: marker_elem marker_elem_marker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY marker_elem
    ADD CONSTRAINT marker_elem_marker_id_fkey FOREIGN KEY (marker_id) REFERENCES marker(id) ON DELETE CASCADE;


--
-- Name: marker_fix marker_fix_marker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY marker_fix
    ADD CONSTRAINT marker_fix_marker_id_fkey FOREIGN KEY (marker_id) REFERENCES marker(id) ON DELETE CASCADE;


--
-- Name: marker marker_source_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY marker
    ADD CONSTRAINT marker_source_fkey FOREIGN KEY (source) REFERENCES source(id);


--
-- Name: source_password source_password_source_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY source_password
    ADD CONSTRAINT source_password_source_fkey FOREIGN KEY (source_id) REFERENCES source(id);


--
-- PostgreSQL database dump complete
--

