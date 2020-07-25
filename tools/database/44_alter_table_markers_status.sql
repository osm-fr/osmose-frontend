ALTER TABLE dynpoi_status RENAME TO markers_status;
ALTER TABLE markers_status RENAME CONSTRAINT dynpoi_status_pkey TO markers_status_pkey;
ALTER TABLE markers_status RENAME COLUMN source TO source_id;
ALTER INDEX idx_dynpoi_status_id RENAME TO idx_markers_status_id;
ALTER INDEX idx_dynpoi_status_source_class RENAME TO idx_markers_status_source_id_class;
