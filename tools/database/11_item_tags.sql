alter table dynpoi_item ADD COLUMN tags varchar[];
UPDATE dynpoi_item SET tags = (SELECT array_agg(tag)
  FROM (
        SELECT
            tag
        FROM
            (SELECT unnest(tags) AS tag, item FROM dynpoi_class WHERE dynpoi_class.item = dynpoi_item.item) AS dynpoi_class
        WHERE
            tag != ''
        GROUP BY tag
        ORDER BY tag
    ) AS a
 );
