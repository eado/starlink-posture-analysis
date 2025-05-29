# Censys Starlink data

Internet scanning data from [Censys](https://censys.com/) is used as our core dataset. 
Censys periodically scans the entire IPv4 space, and, through port scanning and analysis of activity and responses, infers information about the host behind the IPv4 address.
It was contributed by Liz Izhikevich (the instructor for the course) and consists of two tables: 

* `20250407`: contains information about approximately 230 million IPv4 hosts across the public internet
* `20250407_starlink`: contains information about IPv4 hosts on AS 14593 (Starlink) only. Approximately 33k hosts.

Data for both tables was collected by Censys on or around 4/7/2025. The data, containing most Censys host attributes (columns), was loaded into BigQuery, with each row representing a host.

# NIST Vulnerability Database - CVE data

CVE data and a description of affected software / OS was obtained through the [NIST Vulnerability Database](https://nvd.nist.gov/vuln/data-feeds).
To download and reproduce the CVE dataset:

1. Visit https://nvd.nist.gov/vuln/data-feeds, scroll to the section to download JSON feeds (older version, not the JSON 2.0 feeds)
2. download data for 2020 to 2025 as ZIP (i.e., feeds "CVE-2020" to "CVE-2025")
3. unzip all downloaded ZIPs into the same parent directory, the parent directory should directly contain the extracted JSON files
4. Download [jq](https://jqlang.org/) and make sure the jq command-line utility is in your path
5. `cd <parent directory with your unzipped files>`
6. Run the following script:
```sh
for f in *.json; do
    jq -c '.CVE_Items[]' "$f" >> nvdcve.jsonl
done
```
7. Upload `nvdcve.jsonl` to a Google Cloud Storage bucket
8. Load the `nvdcve.jsonl` file from the bucket into a Google BigQuery table (accept default settings, make sure the selected format is "JSON *lines*" or similar), name the table `nvdcve`
