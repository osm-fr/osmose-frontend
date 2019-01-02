DROP INDEX source_country_analyser_analyser2;
ALTER TABLE source DROP COLUMN analyser;
ALTER TABLE source RENAME COLUMN analyser2 TO analyser;
CREATE INDEX source_country_analyser ON source(country, analyser);
