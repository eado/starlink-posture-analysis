CREATE OR REPLACE TABLE `ece-239as-project.starlink.20250407_sample` AS
SELECT *
FROM (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY location.country ORDER BY RAND()) AS row_num
  FROM `ece239as-455719.censys.20250407`
)
WHERE row_num <= 10000
