CREATE TABLE class (
  item integer,
  class integer,
  title hstore,
  level integer,
  timestamp timestamp without time zone,
  tags character varying(255)[],
  PRIMARY KEY(item, class)
);

INSERT INTO class
SELECT
  DISTINCT ON (item, class)
  item,
  class,
  title,
  level,
  timestamp,
  tags
FROM
  dynpoi_class
ORDER BY
  item,
  class,
  timestamp DESC
;

ALTER TABLE dynpoi_class DROP COLUMN title;
ALTER TABLE dynpoi_class DROP COLUMN level;
ALTER TABLE dynpoi_class DROP COLUMN tags;
ALTER TABLE dynpoi_class ADD CONSTRAINT class_item_class_fkey FOREIGN KEY (item, class) REFERENCES class(item, class);

DROP INDEX idx_marker_source_class_z_order_curve;
