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

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

df_baseline_restricted = df_baseline[df_baseline['country'].isin(df_starlink['country'])]

df_proportion_difference = pd.DataFrame(columns=['country', 'proportion_nonstandard_diff'])
df_proportion_difference.set_index('country', inplace=True)  # Modify in place
for country in set(df_starlink.country.values):
    starlink_proportion = df_starlink[df_starlink['country'] == country]['proportion_nonstandard'].iloc[0]
    baseline_proportion = df_baseline[df_baseline['country'] == country]['proportion_nonstandard'].iloc[0]
    df_proportion_difference.loc[country] = starlink_proportion - baseline_proportion

# Create a custom colormap from green (negative) to red (positive)
cmap = mcolors.LinearSegmentedColormap.from_list('green_red', ['green', 'white', 'red'])

# Normalize the colormap to center at 0
norm = mcolors.TwoSlopeNorm(vmin=df_proportion_difference['proportion_nonstandard_diff'].min(),
                            vcenter=0,
                            vmax=df_proportion_difference['proportion_nonstandard_diff'].max())

proportion_diff_world = world.merge(df_proportion_difference, left_on='ADMIN', right_on='country', how='left')
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Plot with the custom colormap
proportion_diff_world.plot(
    column='proportion_nonstandard_diff',
    cmap=cmap,
    linewidth=0.5,
    ax=ax,
    edgecolor='black',
    norm=norm,
    missing_kwds={
        "color": "lightgrey",
        "edgecolor": "black",
        "label": "No data"
    },
    legend=False  # Disable the built-in legend
)

# Manually add a colorbar
cbar = plt.colorbar(ax.collections[0], ax=ax, orientation='horizontal')

# Automatically set colorbar limits based on the plot data
cbar.set_ticks([-0.6, 0, 0.6])  # Custom ticks at -0.6, 0, 0.6
cbar.set_ticklabels(['Less Non-Standard Services (-0.6)', 'Equal (0)', 'More Non-Standard Services (0.6)'])  # Custom tick labels

# Position the colorbar using an xy tuple for flexibility
cbar.ax.set_position([0.15, 0.3, 0.7, 0.03])  # Position in figure: [x, y, width, height]

fig.text(0.5, 0.24, 'Difference in Proportion of Hosts with $\geq$1 Misplaced Ports, (Starlink vs non-Starlink)', ha='center', va='center', fontsize=12)

# Set the title
ax.set_title('Starlink Hosts with Non-IANA Services', fontsize=15)

# Turn off axis
ax.axis('off')

plt.savefig("../figures/fig9_non_IANA_prevalence_diff.png")
