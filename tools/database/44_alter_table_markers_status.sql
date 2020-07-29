ALTER TABLE dynpoi_status RENAME TO markers_status;
ALTER TABLE markers_status RENAME CONSTRAINT dynpoi_status_pkey TO markers_status_pkey;
ALTER TABLE markers_status RENAME COLUMN source TO source_id;
ALTER INDEX idx_dynpoi_status_id RENAME TO idx_markers_status_id;
ALTER INDEX idx_dynpoi_status_source_class RENAME TO idx_markers_status_source_id_class;

ALTER TABLE markers_status ADD COLUMN item integer;
UPDATE markers_status
SET item = markers_counts.item
FROM markers_counts
WHERE
    markers_counts.source_id = markers_status.source_id AND
    markers_counts.class = markers_status.class
;
ALTER TABLE markers_status ALTER COLUMN item SET NOT NULL;
ALTER TABLE markers_status ADD CONSTRAINT markers_status_item_class_fkey FOREIGN KEY (item, class) REFERENCES class (item, class);
