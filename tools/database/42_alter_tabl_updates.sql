ALTER TABLE dynpoi_update RENAME TO updates;
ALTER TABLE updates RENAME CONSTRAINT dynpoi_update_pkey TO updates_pkey;
ALTER TABLE updates RENAME COLUMN source TO source_id;
ALTER TABLE updates ADD CONSTRAINT updates_source_id_fkey FOREIGN KEY (source_id) REFERENCES source (id);

ALTER TABLE dynpoi_update_last RENAME TO updates_last;
ALTER TABLE updates_last RENAME CONSTRAINT dynpoi_update_last_pkey TO updates_last_pkey;
ALTER TABLE updates_last RENAME COLUMN source TO source_id;
ALTER TABLE updates_last ADD CONSTRAINT updates_last_source_id_fkey FOREIGN KEY (source_id) REFERENCES source (id);
