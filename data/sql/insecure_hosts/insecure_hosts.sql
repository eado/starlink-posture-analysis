-- TLS + SMBv1 Insecurity for Starlink Hosts
WITH starlink_insecure AS (
  SELECT 
    location.country_code AS country,
    COUNT(*) AS total,
    COUNTIF(
      service.tls.version_selected IN ('TLSv1_0', 'TLSv1_1')
      OR (
        service.smb.smbv1_support = TRUE OR service.smb.smb_version.major = 1
      )
      OR (
        EXISTS (
            SELECT 1 FROM UNNEST(service.ssh.kex_init_message.client_to_server_ciphers) cipher
            WHERE LOWER(cipher) NOT LIKE '%aes%' AND LOWER(cipher) NOT LIKE '%chacha%'
        )
      )
      OR (
        EXISTS (
            SELECT 1 FROM UNNEST(service.ssh.kex_init_message.client_to_server_ciphers) cipher
            WHERE LOWER(cipher) LIKE '%cbc%'
        )
      )
      OR (
        EXISTS (
            SELECT 1 FROM UNNEST(service.ssh.kex_init_message.server_to_client_ciphers) cipher
            WHERE LOWER(cipher) NOT LIKE '%aes%' AND LOWER(cipher) NOT LIKE '%chacha%'
        )
      )
      OR (
        EXISTS (
            SELECT 1 FROM UNNEST(service.ssh.kex_init_message.server_to_client_ciphers) cipher
            WHERE LOWER(cipher) LIKE '%cbc%'
        )
      )
    ) AS insecure
  FROM `ece239as-455719.censys.20250407_starlink`,
       UNNEST(services) AS service
  WHERE location.country IS NOT NULL
  GROUP BY country
),

-- TLS + SMBv1 Insecurity for All Hosts
all_insecure AS (
  SELECT 
    location.country_code AS country,
    COUNT(*) AS total,
    COUNTIF(
      service.tls.version_selected IN ('TLSv1_0', 'TLSv1_1')
      OR (
        service.smb.smbv1_support = TRUE OR service.smb.smb_version.major = 1
      )
      OR (
        EXISTS (
            SELECT 1 FROM UNNEST(service.ssh.kex_init_message.client_to_server_ciphers) cipher
            WHERE LOWER(cipher) NOT LIKE '%aes%' AND LOWER(cipher) NOT LIKE '%chacha%'
        )
      )
      OR (
        EXISTS (
            SELECT 1 FROM UNNEST(service.ssh.kex_init_message.client_to_server_ciphers) cipher
            WHERE LOWER(cipher) LIKE '%cbc%'
        )
      )
      OR (
        EXISTS (
            SELECT 1 FROM UNNEST(service.ssh.kex_init_message.server_to_client_ciphers) cipher
            WHERE LOWER(cipher) NOT LIKE '%aes%' AND LOWER(cipher) NOT LIKE '%chacha%'
        )
      )
      OR (
        EXISTS (
            SELECT 1 FROM UNNEST(service.ssh.kex_init_message.server_to_client_ciphers) cipher
            WHERE LOWER(cipher) LIKE '%cbc%'
        )
      )
    ) AS insecure
  FROM `ece239as-455719.censys.20250407`,
       UNNEST(services) AS service
  WHERE location.country IS NOT NULL
  GROUP BY country
)

-- Combine both sets
SELECT 
  COALESCE(a.country, s.country) AS country,
  s.total AS starlink_total,
  s.insecure AS starlink_insecure,
  SAFE_DIVIDE(s.insecure, s.total) AS starlink_insecure_rate,
  a.total AS all_total,
  a.insecure AS all_insecure,
  SAFE_DIVIDE(a.insecure, a.total) AS all_insecure_rate
FROM all_insecure a
FULL OUTER JOIN starlink_insecure s
ON a.country = s.country
ORDER BY starlink_insecure_rate DESC

