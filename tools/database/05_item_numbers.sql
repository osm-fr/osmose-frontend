alter table dynpoi_item add column number integer[];
UPDATE dynpoi_item SET number = (SELECT array_agg(n)
                                 FROM (SELECT count(*) AS n FROM dynpoi_class
                                       WHERE dynpoi_class.item = dynpoi_item.item
                                       GROUP BY level
                                       ORDER BY level
                                      ) AS a
                                );

