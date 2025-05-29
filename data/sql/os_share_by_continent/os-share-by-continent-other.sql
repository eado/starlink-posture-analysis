WITH filtered AS (
  SELECT
    location.continent AS continent,
    LOWER(CONCAT(operating_system.vendor, ' ', operating_system.product)) AS os
  FROM
    `ece-239as-project.starlink.20250407_sample`
  WHERE
    operating_system.vendor IS NOT NULL AND 
    operating_system.product IS NOT NULL AND
    location.continent IS NOT NULL
),

os_counts AS (
  SELECT
    continent,
    os,
    COUNT(*) AS count
  FROM
    filtered
  GROUP BY
    continent, os
),

ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY continent ORDER BY count DESC) AS rank
  FROM
    os_counts
),

top_os AS (
  SELECT
    continent,
    os,
    count
  FROM
    ranked
  WHERE
    rank <= 9
),

other_os AS (
  SELECT
    continent,
    '<other>' AS os,
    SUM(count) AS count
  FROM
    ranked
  WHERE
    rank > 9
  GROUP BY
    continent
),

combined AS (
  SELECT * FROM top_os
  UNION ALL
  SELECT * FROM other_os
),

total_per_continent AS (
  SELECT
    continent,
    SUM(count) AS total
  FROM
    combined
  GROUP BY
    continent
)

SELECT
  c.continent,
  c.os,
  ROUND(c.count * 100.0 / t.total, 2) AS percentage_share,
  c.count
FROM
  combined c
JOIN
  total_per_continent t
ON
  c.continent = t.continent
ORDER BY
  continent,
  percentage_share DESC;
