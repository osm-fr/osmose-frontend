CREATE SEQUENCE dynpoi_status_id_seq OWNED BY dynpoi_status.id;
SELECT setval('dynpoi_status_id_seq', max(id)) FROM dynpoi_status;
ALTER TABLE dynpoi_status ALTER id SET DEFAULT NEXTVAL('dynpoi_status_id_seq');
UPDATE dynpoi_status SET id = DEFAULT WHERE id IS NULL;
ALTER TABLE dynpoi_status ADD CONSTRAINT dynpoi_status_id UNIQUE (id);
