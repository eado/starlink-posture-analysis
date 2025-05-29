import matplotlib.pyplot as plt
import numpy as np
import json
from scipy.stats import binom

starlink_data_file = '../data/raw/os_cve_locations/bquxjob_3c73f9c5_1965065a6b9.json'
non_starlink_data_file = '../data/raw/os_cve_locations/bquxjob_5e7c6743_19650747b04.json'


with open(starlink_data_file, 'r') as file:
    starlink_raw_data = json.load(file)

with open(non_starlink_data_file, 'r') as file:
    non_starlink_raw_data = json.load(file)

data = list()

for entry in starlink_raw_data:
    formatted = dict()
    formatted['country'] = entry['country']

    formatted['hosts_with_cve'] = int(entry['hosts_with_cve'])
    formatted['host_count'] = int(entry['host_count'])

    non_entry = next(r for r in non_starlink_raw_data if r['country_code'] == entry['country_code'])
    formatted['non_percent'] = float(non_entry['percentage_with_cve'])

    data.append(formatted)

result = list()
for entry in data:
    if entry['host_count'] < 100:
        continue

    # 1-tailed test
    p_value_upper = binom.sf(max(entry['hosts_with_cve'] - 1, 0),
                             entry['host_count'],
                             entry['non_percent']/100)

    result.append((entry["country"], p_value_upper))

result = sorted(result, key=lambda t: t[1])

print("Country, P-Value")
for t in result:
    print(f'{t[0]}, {t[1]:.3f}')
