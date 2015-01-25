DELETE FROM marker WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%osmosis_railway_crossing%');
DELETE FROM dynpoi_class WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%osmosis_railway_crossing%');
DELETE FROM dynpoi_update_last WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%osmosis_railway_crossing%');
DELETE FROM dynpoi_status WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%osmosis_railway_crossing%');
DELETE FROM dynpoi_source WHERE comment LIKE '%osmosis_railway_crossing%';

DELETE FROM marker WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_merimee%');
DELETE FROM dynpoi_class WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_merimee%');
DELETE FROM dynpoi_update_last WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_merimee%');
DELETE FROM dynpoi_status WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_merimee%');
DELETE FROM dynpoi_source WHERE comment LIKE '%merge_merimee%';

DELETE FROM marker WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_ratp%');
DELETE FROM dynpoi_class WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_ratp%');
DELETE FROM dynpoi_update_last WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_ratp%');
DELETE FROM dynpoi_status WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_ratp%');
DELETE FROM dynpoi_source WHERE comment LIKE '%merge_ratp%';

DELETE FROM marker WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_level_crossing%');
DELETE FROM dynpoi_class WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_level_crossing%');
DELETE FROM dynpoi_update_last WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_level_crossing%');
DELETE FROM dynpoi_status WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_level_crossing%');
DELETE FROM dynpoi_source WHERE comment LIKE '%merge_level_crossing%';

DELETE FROM marker WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_railstation_FR%');
DELETE FROM dynpoi_class WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_railstation_FR%');
DELETE FROM dynpoi_update_last WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_railstation_FR%');
DELETE FROM dynpoi_status WHERE source IN (SELECT source from dynpoi_source WHERE comment LIKE '%merge_railstation_FR%');
DELETE FROM dynpoi_source WHERE comment LIKE '%merge_railstation_FR%';

