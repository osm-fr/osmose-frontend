ALTER INDEX dynpoi_status_pkey RENAME TO dynpoi_status_pkey_old;
CREATE UNIQUE INDEX dynpoi_status_pkey ON dynpoi_status USING btree(source, class, subclass, elems,lat,lon);
ALTER TABLE dynpoi_status DROP CONSTRAINT dynpoi_status_pkey_old;
ALTER TABLE dynpoi_status ADD PRIMARY KEY USING INDEX dynpoi_status_pkey;
