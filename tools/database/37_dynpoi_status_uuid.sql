DELETE FROM
  dynpoi_status
WHERE uuid IN (
  SELECT
    uuid
  FROM
    dynpoi_status
  GROUP BY
    uuid
  HAVING
    count(*) >= 2
);

ALTER TABLE dynpoi_status DROP CONSTRAINT dynpoi_status_pkey;
ALTER TABLE dynpoi_status ADD PRIMARY KEY (uuid);
CREATE INDEX idx_dynpoi_status_source_class ON dynpoi_status(source, class);
