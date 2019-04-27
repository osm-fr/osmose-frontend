CREATE TABLE stats AS
SELECT
  source,
  class,
  count,
  tsrange(t, lead(t) OVER(PARTITION BY source, class)) AS timestamp_range
FROM (
  SELECT
    source,
    class,
    count,
    CASE
      WHEN
        lag(count) OVER(PARTITION BY source, class ORDER BY source, class, timestamp) IS NULL OR
        lag(count) OVER(PARTITION BY source, class ORDER BY source, class, timestamp) != count
      THEN timestamp
    END AS t
  FROM
    dynpoi_stats
  ORDER BY
    source,
    class,
    timestamp
) AS t
WHERE
  t IS NOT NULL
ORDER BY
    source,
    class,
    t
;

CREATE INDEX idx_stats ON stats(source, class);

DROP TABLE dynpoi_stats;
