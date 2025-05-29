import matplotlib.pyplot as plt
import numpy as np
import json

starlink_data_file = '../data/raw/os_cve_locations/bquxjob_3c73f9c5_1965065a6b9.json'
non_starlink_data_file = '../data/raw/os_cve_locations/bquxjob_5e7c6743_19650747b04.json'


with open(starlink_data_file, 'r') as file:
    starlink_raw_data = json.load(file)

with open(non_starlink_data_file, 'r') as file:
    non_starlink_raw_data = json.load(file)

starlink_filtered = list(filter(lambda r: int(r['host_count']) > 100, starlink_raw_data))[:12]

data = list()

for entry in starlink_filtered:
    formatted = dict()
    formatted['country'] = entry['country']

    formatted['percent'] = float(entry['percentage_with_cve'])

    non_entry = next(r for r in non_starlink_raw_data if r['country_code'] == entry['country_code'])
    formatted['non_percent'] = float(non_entry['percentage_with_cve'])

    data.append(formatted)

# Extract components
countries = [entry['country'] for entry in data]
percent = [entry['percent'] for entry in data]
non_percent = [entry['non_percent'] for entry in data]

# Y positions for bar pairs
y = np.arange(len(countries))
bar_height = 0.4

fig, ax = plt.subplots(figsize=(6, 6))

# Draw IPv6-style (blue) slightly lower
ax.barh(y + bar_height/2, non_percent, height=bar_height, color='blue', label='Non-Starlink Hosts')

# Draw IPv4-style (red) slightly higher
ax.barh(y - bar_height/2, percent, height=bar_height, color='red', label='Starlink Hosts')

# Formatting
ax.set_yticks(y)
ax.set_yticklabels(countries)
ax.invert_yaxis()
ax.set_xlabel('Fraction of Hosts Affected by OS-Related CVEs (%)')
#ax.set_xscale('log')
ax.set_xlim(0, 2)
#ax.set_title('Percent vs Non-Percent by Country')
ax.legend()
#ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

plt.tight_layout()
plt.savefig('../figures/fig2_disparity_insecure_os.png')
