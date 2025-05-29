# Censys Starlink data

TODO explain what Censys is, we got data from Liz dated 20250407, blah blh

# NVD Starlink data

TODO put in actual english--

https://nvd.nist.gov/vuln/data-feeds , get the JSON feeds and not the JSON2.0 feeds 
download 2020 to 2025 as ZIP, unzip

make sure jq utility is in your path https://jqlang.org/

```sh
for f in *.json; do
    jq -c '.CVE_Items[]' "$f" >> nvdcve.jsonl
done
```

upload to bigquery
