ALTER TABLE marker RENAME TO markers;
ALTER TABLE markers RENAME COLUMN source TO source_id;
ALTER TABLE markers RENAME CONSTRAINT marker_pkey TO markers_pkey;
ALTER TABLE markers RENAME CONSTRAINT marker_source_fkey TO markers_sources_fkey;
ALTER TABLE markers DROP CONSTRAINT marker_class_fkey;
ALTER TABLE markers ADD CONSTRAINT markers_item_class_fkey FOREIGN KEY (item, class) REFERENCES class (item, class);
