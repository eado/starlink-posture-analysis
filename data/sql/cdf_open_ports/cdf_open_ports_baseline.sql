WITH filtered AS (
  SELECT
    location.continent AS continent,
    ARRAY_LENGTH(ports_list) AS num_open_ports
  FROM
    -- `ece239as-455719.censys.20250407_starlink`
    `ece-239as-project.starlink.20250407_sample`
  WHERE
    ports_list IS NOT NULL AND
    location.continent IS NOT NULL
),
ranked AS (
  SELECT
    continent,
    num_open_ports,
    COUNT(*) AS count_per_value
  FROM
    filtered
  GROUP BY
    continent, num_open_ports
),
cdf AS (
  SELECT
    continent,
    num_open_ports,
    count_per_value,
    SUM(count_per_value) OVER (PARTITION BY continent ORDER BY num_open_ports) AS cumulative_count,
    SUM(count_per_value) OVER (PARTITION BY continent) AS total_count
  FROM
    ranked
)
SELECT
  continent,
  num_open_ports,
  cumulative_count / total_count AS cdf
FROM
  cdf
ORDER BY
  continent,
  num_open_ports;