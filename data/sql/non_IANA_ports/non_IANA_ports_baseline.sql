WITH iana_ports AS (
  SELECT * FROM UNNEST([
    STRUCT('http' AS service_name, 80 AS port),
    ('https', 443),
    ('ssh', 22),
    ('ftp', 21),
    ('telnet', 23),
    ('smtp', 25),
    ('imap', 143),
    ('pop3', 110),
    ('dns', 53),
    ('mysql', 3306),
    ('rdp', 3389),
    ('mongodb', 27017),
    ('redis', 6379),
    ('postgresql', 5432),
    ('vnc', 5900)
  ])
),

flattened_services AS (
  SELECT
    host_identifier.ipv4 AS ipv4,
    service.port,
    service.service_name,
    location.country
  FROM
    -- `ece239as-455719.censys.20250407_starlink`,
    `ece-239as-project.starlink.20250407_sample`,
    UNNEST(services) AS service
),

mismatched_services AS (
  SELECT
    ipv4,
    country,
    LOWER(f.service_name) AS service_name
  FROM
    flattened_services f
  JOIN
    iana_ports i
  ON
    LOWER(f.service_name) = LOWER(i.service_name)
  WHERE
    f.port != i.port
),

hosts_with_mismatch AS (
  SELECT DISTINCT ipv4, country FROM mismatched_services
),

total_hosts_by_country AS (
  SELECT
    country,
    COUNT(DISTINCT ipv4) AS total_hosts
  FROM
    flattened_services
  GROUP BY
    country
),

mismatched_counts AS (
  SELECT
    country,
    COUNT(DISTINCT ipv4) AS hosts_with_nonstandard_ports
  FROM
    hosts_with_mismatch
  GROUP BY
    country
),

service_mismatch_breakdown AS (
  SELECT
    country,
    service_name,
    COUNT(*) AS mismatch_count
  FROM
    mismatched_services
  GROUP BY
    country, service_name
),

pivoted_service_proportions AS (
  SELECT
    country,
    -- Replace NULLs with 0 and divide by total for percentage
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'http' THEN mismatch_count END), SUM(mismatch_count)) AS pct_http,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'https' THEN mismatch_count END), SUM(mismatch_count)) AS pct_https,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'ssh' THEN mismatch_count END), SUM(mismatch_count)) AS pct_ssh,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'ftp' THEN mismatch_count END), SUM(mismatch_count)) AS pct_ftp,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'telnet' THEN mismatch_count END), SUM(mismatch_count)) AS pct_telnet,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'smtp' THEN mismatch_count END), SUM(mismatch_count)) AS pct_smtp,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'imap' THEN mismatch_count END), SUM(mismatch_count)) AS pct_imap,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'pop3' THEN mismatch_count END), SUM(mismatch_count)) AS pct_pop3,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'dns' THEN mismatch_count END), SUM(mismatch_count)) AS pct_dns,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'mysql' THEN mismatch_count END), SUM(mismatch_count)) AS pct_mysql,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'rdp' THEN mismatch_count END), SUM(mismatch_count)) AS pct_rdp,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'mongodb' THEN mismatch_count END), SUM(mismatch_count)) AS pct_mongodb,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'redis' THEN mismatch_count END), SUM(mismatch_count)) AS pct_redis,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'postgresql' THEN mismatch_count END), SUM(mismatch_count)) AS pct_postgresql,
    SAFE_DIVIDE(SUM(CASE WHEN service_name = 'vnc' THEN mismatch_count END), SUM(mismatch_count)) AS pct_vnc
  FROM
    service_mismatch_breakdown
  GROUP BY
    country
)

SELECT
  c.country,
  c.hosts_with_nonstandard_ports,
  t.total_hosts,
  SAFE_DIVIDE(c.hosts_with_nonstandard_ports, t.total_hosts) AS proportion_nonstandard,
  -- Explicitly select all percentage columns to avoid duplicate 'country'
  p.pct_http,
  p.pct_https,
  p.pct_ssh,
  p.pct_ftp,
  p.pct_telnet,
  p.pct_smtp,
  p.pct_imap,
  p.pct_pop3,
  p.pct_dns,
  p.pct_mysql,
  p.pct_rdp,
  p.pct_mongodb,
  p.pct_redis,
  p.pct_postgresql,
  p.pct_vnc
FROM
  mismatched_counts c
JOIN
  total_hosts_by_country t ON c.country = t.country
LEFT JOIN
  pivoted_service_proportions p ON c.country = p.country
ORDER BY
  proportion_nonstandard DESC;
