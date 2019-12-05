ALTER TABLE class ALTER COLUMN title TYPE jsonb USING hstore_to_json(title);
ALTER TABLE dynpoi_categ ALTER COLUMN menu TYPE jsonb USING hstore_to_json(menu);
ALTER TABLE dynpoi_item ALTER COLUMN menu TYPE jsonb USING hstore_to_json(menu);
ALTER TABLE dynpoi_status ALTER COLUMN subtitle TYPE jsonb USING hstore_to_json(subtitle);
ALTER TABLE marker ALTER COLUMN subtitle TYPE jsonb USING hstore_to_json(subtitle);
ALTER TABLE marker_elem ALTER COLUMN tags TYPE jsonb USING hstore_to_json(tags);
ALTER TABLE marker_fix ALTER COLUMN tags_create TYPE jsonb USING hstore_to_json(tags_create);
ALTER TABLE marker_fix ALTER COLUMN tags_modify TYPE jsonb USING hstore_to_json(tags_modify);
