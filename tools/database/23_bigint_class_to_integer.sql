UPDATE dynpoi_stats SET class = class % 2147483647 WHERE class != class % 2147483647;
ALTER TABLE dynpoi_stats ALTER COLUMN class TYPE integer;

UPDATE dynpoi_class SET class = class % 2147483647 WHERE class != class % 2147483647;
ALTER TABLE dynpoi_class ALTER COLUMN class TYPE integer;
