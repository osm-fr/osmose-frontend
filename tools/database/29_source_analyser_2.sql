ALTER TABLE source ADD analyser2 character varying(256);
CREATE INDEX source_country_analyser_analyser2 ON source(country, analyser, analyser2);
DROP INDEX source_country_analyser;
