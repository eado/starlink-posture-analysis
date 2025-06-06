import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Load CSV files
df_baseline = pd.read_csv("../data/raw/cdf_open_ports/csv_baseline.csv")
df_starlink = pd.read_csv("../data/raw/cdf_open_ports/csv_starlink.csv")

# Identify all unique continents across both datasets
all_continents = sorted(set(df_baseline['continent']).union(df_starlink['continent']))
colors = plt.get_cmap('tab10')
continent_colors = {continent: colors(i % 10) for i, continent in enumerate(all_continents)}

def plot_cdf_by_continent(ax, df, title, show_xlabel=True):
    df = df.sort_values(['continent', 'num_open_ports'])
    min_x = df['num_open_ports'].replace(0, np.nan).min()
    max_x = df['num_open_ports'].max()
    x_vals = np.logspace(np.log10(min_x), np.log10(max_x), 300)

    # Track Asia intercept
    asia_intercept_x = None

    for continent, group in df.groupby('continent'):
        group = group[group['num_open_ports'] > 0]
        interp_fn = interp1d(group['num_open_ports'], group['cdf'], kind='linear',
                             bounds_error=False, fill_value=(0, 1))
        y_vals = interp_fn(x_vals)
        ax.plot(x_vals, y_vals, label=continent, color=continent_colors[continent])

        # Save x where Asia curve crosses y = 0.9
        if continent == "Asia":
            try:
                inv_interp = interp1d(y_vals, x_vals, bounds_error=False)
                asia_intercept_x = inv_interp(0.9)
            except Exception:
                pass  # if interpolation fails, skip marking

    ax.set_xscale('log')
    ax.set_ylim(0, 1)
    if show_xlabel:
        ax.set_xlabel('Number of Open Ports (log scale)')
    ax.set_ylabel('CDF')
    ax.legend(title='Continent', loc='lower right', fontsize=9, title_fontsize=10, frameon=True)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Add vertical subplot title
    ax.text(-0.1, 0.5, title, transform=ax.transAxes,
            fontsize=12, va='center', ha='center', rotation=90)

    # Draw horizontal line at y = 0.9
    ax.axhline(0.9, color='gray', linestyle=':', linewidth=1)

    # Mark Asia intercept if available
    # if asia_intercept_x is not None and not np.isnan(asia_intercept_x):
    #     ax.axvline(asia_intercept_x, color=continent_colors["Asia"], linestyle=':', linewidth=1)
    #     ax.plot(asia_intercept_x, 0.9, 'o', color=continent_colors["Asia"])
    #     ax.text(asia_intercept_x, 0.91, f'{asia_intercept_x:.1f}', color=continent_colors["Asia"],
    #             fontsize=9, ha='center')
    # if ax == ax2: ax.set_xlabel('Number of Open Ports (log scale)')


# Create subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
fig.suptitle('CDF of Open Ports per Continent', fontsize=16)
# Plot each dataset
plot_cdf_by_continent(ax2, df_baseline, 'Non-Starlink Hosts', show_xlabel=True)
plot_cdf_by_continent(ax1, df_starlink, 'Starlink Hosts', show_xlabel=False)

# Tight layout
plt.subplots_adjust(left=0.18, right=0.98, hspace=0.1)
plt.tight_layout()
plt.savefig("../figures/fig7_open_ports_cdfs.png")
