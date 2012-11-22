--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: dynpoi_categ; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE dynpoi_categ (
    categ integer NOT NULL,
    menu hstore
);


--
-- Name: dynpoi_class; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE dynpoi_class (
    source integer,
    class bigint,
    item integer,
    title hstore,
    level integer
);


--
-- Name: dynpoi_item; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE dynpoi_item (
    item integer NOT NULL,
    categ integer,
    marker_color character varying(16),
    marker_flag character varying(16),
    menu hstore,
    levels integer[],
    number integer[]
);


--
-- Name: dynpoi_source; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE dynpoi_source (
    source integer NOT NULL,
    update character varying(128),
    contact character varying(256),
    comment character varying(1024),
    updated boolean
);


--
-- Name: dynpoi_stats; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE dynpoi_stats (
    source integer NOT NULL,
    class bigint NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    count integer
);


--
-- Name: dynpoi_status; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE dynpoi_status (
    source integer NOT NULL,
    class integer NOT NULL,
    subclass integer NOT NULL,
    elems character varying(128) NOT NULL,
    date timestamp with time zone,
    status character varying(128),
    lat integer,
    lon integer,
    subtitle hstore
);


--
-- Name: dynpoi_update; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE dynpoi_update (
    source integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    remote_url character varying(2048),
    remote_ip character varying(128)
);


--
-- Name: dynpoi_update_last; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE dynpoi_update_last (
    source integer NOT NULL,
    "timestamp" timestamp with time zone
);


--
-- Name: marker; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE marker (
    id bigint NOT NULL,
    source integer,
    class integer,
    subclass integer,
    lat integer,
    lon integer,
    elems text,
    item integer,
    subtitle hstore
);


--
-- Name: marker_elem; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE marker_elem (
    marker_id bigint NOT NULL,
    elem_index integer NOT NULL,
    data_type character(1),
    id bigint,
    tags hstore,
    username text
);


--
-- Name: marker_fix; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE marker_fix (
    marker_id bigint NOT NULL,
    diff_index integer NOT NULL,
    elem_data_type character(1),
    elem_id bigint,
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
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: marker_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE marker_id_seq OWNED BY marker.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY marker ALTER COLUMN id SET DEFAULT nextval('marker_id_seq'::regclass);


--
-- Name: dynpoi_categ_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dynpoi_categ
    ADD CONSTRAINT dynpoi_categ_pkey PRIMARY KEY (categ);

ALTER TABLE dynpoi_categ CLUSTER ON dynpoi_categ_pkey;


--
-- Name: dynpoi_item_marker; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dynpoi_item
    ADD CONSTRAINT dynpoi_item_marker UNIQUE (marker_color, marker_flag);


--
-- Name: dynpoi_item_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dynpoi_item
    ADD CONSTRAINT dynpoi_item_pkey PRIMARY KEY (item);

ALTER TABLE dynpoi_item CLUSTER ON dynpoi_item_pkey;


--
-- Name: dynpoi_source_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dynpoi_source
    ADD CONSTRAINT dynpoi_source_pkey PRIMARY KEY (source);


--
-- Name: dynpoi_source_update_unique; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dynpoi_source
    ADD CONSTRAINT dynpoi_source_update_unique UNIQUE (update);


--
-- Name: dynpoi_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dynpoi_stats
    ADD CONSTRAINT dynpoi_stats_pkey PRIMARY KEY (source, class, "timestamp");

ALTER TABLE dynpoi_stats CLUSTER ON dynpoi_stats_pkey;


--
-- Name: dynpoi_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dynpoi_status
    ADD CONSTRAINT dynpoi_status_pkey PRIMARY KEY (source, class, subclass, elems);

ALTER TABLE dynpoi_status CLUSTER ON dynpoi_status_pkey;


--
-- Name: dynpoi_update_last_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dynpoi_update_last
    ADD CONSTRAINT dynpoi_update_last_pkey PRIMARY KEY (source);


--
-- Name: dynpoi_update_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dynpoi_update
    ADD CONSTRAINT dynpoi_update_pkey PRIMARY KEY (source, "timestamp");


--
-- Name: marker_elem_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY marker_elem
    ADD CONSTRAINT marker_elem_pkey PRIMARY KEY (marker_id, elem_index);

ALTER TABLE marker_elem CLUSTER ON marker_elem_pkey;


--
-- Name: marker_fix_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY marker_fix
    ADD CONSTRAINT marker_fix_pkey PRIMARY KEY (marker_id, diff_index);

ALTER TABLE marker_fix CLUSTER ON marker_fix_pkey;


--
-- Name: marker_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY marker
    ADD CONSTRAINT marker_pkey PRIMARY KEY (id);

ALTER TABLE marker CLUSTER ON marker_pkey;


--
-- Name: dynpoi_source_comment_unique; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX dynpoi_source_comment_unique ON dynpoi_source USING btree (comment);


--
-- Name: dynpoi_stats_timestamp; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX dynpoi_stats_timestamp ON dynpoi_stats USING btree ("timestamp");


--
-- Name: idx_dynpoi_class_class; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_dynpoi_class_class ON dynpoi_class USING btree (class);

ALTER TABLE dynpoi_class CLUSTER ON idx_dynpoi_class_class;


--
-- Name: idx_dynpoi_class_item; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_dynpoi_class_item ON dynpoi_class USING btree (item);


--
-- Name: idx_dynpoi_class_source; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_dynpoi_class_source ON dynpoi_class USING btree (source);


--
-- Name: idx_dynpoi_class_source_class; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_dynpoi_class_source_class ON dynpoi_class USING btree (source, class);


--
-- Name: idx_dynpoi_update_source; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_dynpoi_update_source ON dynpoi_update USING btree (source);


--
-- Name: idx_dynpoi_update_timestamp; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_dynpoi_update_timestamp ON dynpoi_update USING btree ("timestamp");


--
-- Name: idx_marker_elem_data_type_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_marker_elem_data_type_id ON marker_elem USING btree (data_type, id);


--
-- Name: idx_marker_elem_username; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_marker_elem_username ON marker_elem USING btree (username);


--
-- Name: idx_marker_item; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_marker_item ON marker USING btree (item);


--
-- Name: idx_marker_lat; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_marker_lat ON marker USING btree (lat);


--
-- Name: idx_marker_lon; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_marker_lon ON marker USING btree (lon);


--
-- Name: idx_marker_source_class; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_marker_source_class ON marker USING btree (source, class);


--
-- Name: idx_marker_source_class_subclass_lat_lon_elems; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX idx_marker_source_class_subclass_lat_lon_elems ON marker USING btree (source, class, subclass, lat, lon, elems);


--
-- Name: marker_elem_marker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY marker_elem
    ADD CONSTRAINT marker_elem_marker_id_fkey FOREIGN KEY (marker_id) REFERENCES marker(id) ON DELETE CASCADE;


--
-- Name: marker_fix_marker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY marker_fix
    ADD CONSTRAINT marker_fix_marker_id_fkey FOREIGN KEY (marker_id) REFERENCES marker(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

