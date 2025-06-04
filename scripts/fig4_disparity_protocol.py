import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import geopandas as gpd

data = pd.read_csv("../data/raw/insecure_hosts/insecure_hosts.csv")
data["insecure_ratio"] = data["starlink_insecure_rate"] / data["all_insecure_rate"]
data = data.dropna()

world = gpd.read_file("../data/raw/ne_110m_admin_0_sovereignty/ne_110m_admin_0_sovereignty.shp")
world = world.rename(columns={"ISO_A2_EH": "country"})

# Aggregate by continent and merge with your data
world_continents = world.dissolve(by='country').reset_index()
merged = world_continents.merge(data, on='country', how='left')

# Normalize the color: green if <1, red if >1
def get_color(value):
    if pd.isna(value):
        return '#cccccc'
    elif value < 1:
        # More green the smaller it gets (0.2 = dark green)
        return mcolors.to_hex(plt.cm.Greens(1 - value))
    else:
        # More red the larger it gets (2.5 = dark red)
        norm = min(value / 2.5, 1)  # cap at 2.5 for colormap
        return mcolors.to_hex(plt.cm.Reds(norm))

merged['color'] = merged['insecure_ratio'].apply(get_color)


# Create a custom colorbar legend
fig, ax = plt.subplots(figsize=(12, 6))
merged.plot(ax=ax, color=merged['color'], edgecolor='black')

# Title and formatting
plt.title('Starlink Insecurity Ratio by Country', fontsize=14)
plt.axis('off')

# Create a colorbar gradient (from green to red)
cmap = mcolors.LinearSegmentedColormap.from_list("custom", [plt.cm.Greens(0.8), plt.cm.Greens(0.3), plt.cm.Reds(0.4), plt.cm.Reds(0.8)])
norm = mcolors.Normalize(vmin=0, vmax=2.5)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])

# Add colorbar
cbar = fig.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.046, pad=0.04)
cbar.set_label('Insecurity Ratio (Starlink vs non-Starlink)', fontsize=12)
cbar.set_ticks([0, 1, 2.5])
cbar.set_ticklabels(['More Secure (<1)', 'Equal (1)', 'Less Secure (>2.5)'])


# Add title
plt.title('Starlink Insecurity Ratio by Country', fontsize=14)
plt.axis('off')
plt.savefig('../figures/fig4_disparity_protocol.png')

