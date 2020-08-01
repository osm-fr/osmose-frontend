ALTER TABLE stats RENAME COLUMN source TO source_id;
ALTER TABLE stats ADD CONSTRAINT stats_source_id_fkey FOREIGN KEY (source_id) REFERENCES sources (id);

ALTER TABLE backend RENAME TO backends;
