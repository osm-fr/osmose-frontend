alter table dynpoi_item ADD COLUMN levels integer[];
UPDATE dynpoi_item SET levels = (SELECT array_agg(level)
                                 FROM (SELECT level FROM dynpoi_class
                                       WHERE dynpoi_class.item = dynpoi_item.item
                                       GROUP BY level
                                       ORDER BY level
                                      ) AS a
                                );

