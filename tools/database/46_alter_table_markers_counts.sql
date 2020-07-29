ALTER TABLE dynpoi_class RENAME TO markers_counts;
ALTER TABLE markers_counts RENAME COLUMN source TO source_id;
ALTER TABLE markers_counts RENAME CONSTRAINT dynpoi_class_pkey TO markers_counts_pkey;
ALTER TABLE markers_counts RENAME CONSTRAINT dynpoi_class_source_fkey TO markers_counts_source_id_fkey;
ALTER TABLE markers_counts RENAME CONSTRAINT class_item_class_fkey TO markers_counts_item_class_fkey;
ALTER TABLE markers_counts DROP COLUMN timestamp;
