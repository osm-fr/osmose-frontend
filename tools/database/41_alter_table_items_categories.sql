ALTER TABLE dynpoi_categ RENAME TO categories;
ALTER TABLE categories RENAME CONSTRAINT dynpoi_categ_pkey TO categories_pkey;
ALTER TABLE categories RENAME COLUMN categ to id;

ALTER TABLE dynpoi_item RENAME TO items;
ALTER TABLE items RENAME CONSTRAINT dynpoi_item_pkey TO items_pkey;
ALTER TABLE items RENAME CONSTRAINT dynpoi_item_marker TO items_marker_color_flag;
ALTER TABLE items RENAME COLUMN categ TO categorie_id;
ALTER TABLE items ALTER COLUMN categorie_id SET NOT NULL;
ALTER TABLE items ADD CONSTRAINT item_categorie_fkey FOREIGN KEY (categorie_id) REFERENCES categories (id);
