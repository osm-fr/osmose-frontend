ALTER TABLE dynpoi_update_last ADD COLUMN version text DEFAULT NULL;
ALTER TABLE dynpoi_update_last ADD COLUMN remote_ip character varying(128) DEFAULT NULL;

UPDATE dynpoi_update_last SET version = (SELECT version FROM dynpoi_update WHERE dynpoi_update.source = dynpoi_update_last.source ORDER BY timestamp DESC limit 1) WHERE version IS NULL;
UPDATE dynpoi_update_last SET remote_ip = (SELECT remote_ip FROM dynpoi_update WHERE dynpoi_update.source = dynpoi_update_last.source ORDER BY timestamp DESC limit 1) WHERE remote_ip IS NULL;
