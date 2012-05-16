ALTER TABLE dynpoi_categ ADD COLUMN menu hstore;
UPDATE dynpoi_categ SET menu = hstore('fr', menu_fr) || hstore('en', menu_en);

ALTER TABLE dynpoi_class ADD COLUMN title hstore;
UPDATE dynpoi_class SET title = hstore('fr', title_fr) || hstore('en', title_en);

ALTER TABLE dynpoi_item ADD COLUMN menu hstore;
UPDATE dynpoi_item SET menu = hstore('fr', menu_fr) || hstore('en', menu_en);

ALTER TABLE dynpoi_status ADD COLUMN subtitle hstore;
UPDATE dynpoi_status SET subtitle = hstore('fr', subtitle_fr) || hstore('en', subtitle_en);

