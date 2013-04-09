ALTER TABLE dynpoi_class ADD COLUMN count integer;

UPDATE dynpoi_class
SET count = (SELECT count(*) FROM marker
             WHERE marker.source = dynpoi_class.source AND
                   marker.class = dynpoi_class.class);

