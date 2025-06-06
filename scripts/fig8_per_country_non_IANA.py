import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Path to the downloaded shapefile (adjust this path as needed)
shapefile_path = '../data/mapfiles/ne_110m_admin_0_countries.shp'

# Load the shapefile manually
world = gpd.read_file(shapefile_path)

# Assume df_starlink has columns: country, hosts_with_nonstandard_ports, total_hosts, proportion_nonstandard
df_starlink = pd.read_csv('../data/raw/non_IANA_ports/nonstandard_ports_starlink.csv')
df_baseline = pd.read_csv('../data/raw/non_IANA_ports/nonstandard_ports_baseline.csv')

# df_starlink = pd.read_csv('data/test.csv')

# Strip and align country names if necessary
df_starlink['country'] = df_starlink['country'].str.strip()
df_baseline['country'] = df_baseline['country'].str.strip()


country_mapping = {
    'United States': 'United States of America',
    'Samoa': 'Samoa',
    'Malta': 'Malta',
    'Dominican Republic': 'Dominican Republic',
    'Czech Republic': 'Czechia',
    'South Sudan': 'South Sudan',
    'Cape Verde': 'Cabo Verde',
    'Solomon Islands': 'Solomon Islands',
    # 'Reunion': 'France',  # Réunion is an overseas department of France
    'Singapore': 'Singapore',
    # 'Saint Martin': 'France',  # Likely Saint Martin (French part), part of France
    # 'Guernsey': 'United Kingdom',  # Crown dependency, not separately listed
    # 'Martinique': 'France',
    # 'Mayotte': 'France',
    # 'Guadeloupe': 'France',
    'Tuvalu': 'Tuvalu',
    # 'Guam': 'United States of America',
    'Barbados': 'Barbados',
    'Tonga': 'Tonga',
    'Swaziland': 'Eswatini',
    # 'Cook Islands': 'New Zealand',  # Free association with New Zealand
    # 'Saint Barthelemy': 'France',
    'Maldives': 'Maldives',
    # 'French Guiana': 'France',
    # 'U.S. Virgin Islands': 'United States of America',
    'Macedonia': 'North Macedonia'
}

# Resolve naming issues between censys and geopandas
df_starlink['country'] = df_starlink['country'].replace(country_mapping)
df_baseline['country'] = df_baseline['country'].replace(country_mapping)

# Merge your data with the map
merged_starlink = world.merge(df_starlink, left_on='ADMIN', right_on='country', how='left')
merged_baseline = world.merge(df_baseline, left_on='ADMIN', right_on='country', how='left')

# print(merged_starlink.columns)

df_starlink.set_index('country')
df_baseline.set_index('country')

################################### END OF DATAFRAME DEFINITIONS #############################################################################################################################################################

pd.set_option('future.no_silent_downcasting', True)

# List of service columns to consider
service_cols = [
    'pct_http', 'pct_https', 'pct_ssh', 'pct_ftp', 'pct_telnet', 'pct_smtp',
    'pct_imap', 'pct_pop3', 'pct_dns', 'pct_mysql', 'pct_rdp',
    'pct_mongodb', 'pct_redis', 'pct_postgresql', 'pct_vnc'
]

# Only include services that have at least some non-null data
available_services = [col for col in service_cols if df_starlink[col].notnull().sum() > 0]

# Pick top N countries by mismatch volume (e.g. 12 for a 4x3 grid)
top_countries = df_starlink.sort_values('hosts_with_nonstandard_ports', ascending=False).head(35)
top_countries = df_starlink.sort_values('hosts_with_nonstandard_ports', ascending=False).head(6)
# bottom_countries = df_starlink.sort_values('hosts_with_nonstandard_ports', ascending=False).tail(12)

top_countries = pd.concat([top_countries, df_starlink[df_starlink['country']=='Peru'], df_starlink[df_starlink['country']=='Philippines']])

# Setup subplot grid
n_countries = len(top_countries)
n_cols = 4
n_rows = int(np.ceil(n_countries / n_cols))

fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, n_rows * 2.8), sharex=True)
axes = axes.flatten()

for i, (idx, row) in enumerate(top_countries.iterrows()):
    ax = axes[i]
    values = row[available_services].fillna(0)
    ax.barh([svc.replace('pct_', '').upper() for svc in available_services], values)
    
    # Title with increased font size
    ax.set_title(f"{row['country']}\n(n={row['hosts_with_nonstandard_ports']})", fontsize=13)

    # Hide y-axis labels except in leftmost column
    if i % n_cols != 0:
        ax.set_yticklabels([])
        ax.tick_params(axis='y', left=False)

    # Styling
    ax.set_xlim(0, 1)
    ax.invert_yaxis()
    ax.tick_params(axis='x')
    ax.grid(True, axis='both')


# Hide unused subplots if there are any
for j in range(i + 1, len(axes)):
    axes[j].axis('off')

fig.suptitle('Top Services Contributing to Non-IANA Port Usage on Starlink Hosts by Country', fontsize=16)
plt.tight_layout(rect=[0, 0, 1, .99])
# plt.show()
plt.savefig("../figures/fig8_per_country_non_IANA.png")