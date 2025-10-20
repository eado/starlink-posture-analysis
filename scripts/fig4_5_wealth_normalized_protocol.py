import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import geopandas as gpd
import numpy as np
from sklearn.linear_model import LinearRegression

# Load insecure hosts data
data = pd.read_csv("../data/raw/insecure_hosts/insecure_hosts_plus.csv")
data["insecure_ratio"] = data["starlink_insecure_rate"] / data["all_insecure_rate"]
data = data.dropna()

# Load wealth data for normalization
affluent = pd.read_csv("../data/raw/affluent/affluent.csv")
# Clean the median wealth column (remove quotes, estimates, and convert to numeric)
affluent['Median'] = (affluent['Median'].str.replace('"', '')
                                        .str.replace(',', '')
                                        .str.replace(r'\s*\(est\.\)', '', regex=True))
# Convert to numeric, setting invalid values to NaN
affluent['Median'] = pd.to_numeric(affluent['Median'], errors='coerce')

# Merge with wealth data using country names
data_with_wealth = data.merge(affluent[['Location', 'Median']],
                              left_on='country_name', right_on='Location', how='left')

# Remove countries without wealth data for regression
regression_data = data_with_wealth.dropna(subset=['Median', 'insecure_ratio']).copy()

# Transform wealth to log scale for better linear relationship
regression_data['log_median_wealth'] = np.log10(regression_data['Median'])

# Fit linear regression: insecurity_ratio ~ log(median_wealth)
X = regression_data[['log_median_wealth']]
y = regression_data['insecure_ratio']
model = LinearRegression().fit(X, y)

# Predict expected insecurity for all countries with wealth data
data_with_wealth['log_median_wealth'] = np.log10(data_with_wealth['Median'])
mask = ~data_with_wealth['log_median_wealth'].isna()
data_with_wealth.loc[mask, 'expected_insecurity'] = model.predict(data_with_wealth.loc[mask, ['log_median_wealth']])

# Calculate residuals (actual - expected)
data_with_wealth['insecurity_residual'] = data_with_wealth['insecure_ratio'] - data_with_wealth['expected_insecurity']

# Use residuals for coloring instead of raw ratios
data = data_with_wealth.copy()
data['insecure_ratio'] = data['insecurity_residual']

world = gpd.read_file("../data/raw/ne_110m_admin_0_sovereignty/ne_110m_admin_0_sovereignty.shp")
world = world.rename(columns={"ISO_A2_EH": "country"})

# Aggregate by continent and merge with your data
world_continents = world.dissolve(by='country').reset_index()
merged = world_continents.merge(data, on='country', how='left')

# Color based on residuals: green if below expected (better than expected), red if above expected (worse than expected)
def get_color(residual):
    if pd.isna(residual):
        return '#cccccc'
    elif residual < 0:
        # Better than expected - green (more negative = darker green)
        intensity = min(abs(residual) / 0.5, 1)  # cap at 0.5 for colormap
        return mcolors.to_hex(plt.cm.Greens(intensity))
    else:
        # Worse than expected - red (more positive = darker red)
        intensity = min(residual / 0.5, 1)  # cap at 0.5 for colormap
        return mcolors.to_hex(plt.cm.Reds(intensity))

merged['color'] = merged['insecure_ratio'].apply(get_color)


# Create a custom colorbar legend
fig, ax = plt.subplots(figsize=(12, 6))
merged.plot(ax=ax, color=merged['color'], edgecolor='black')

# Title and formatting
plt.title('Starlink Insecurity: Deviation from Wealth-Expected Levels', fontsize=14)
plt.axis('off')

# Create a colorbar gradient (from green through white to red)
cmap = mcolors.LinearSegmentedColormap.from_list("custom", [plt.cm.Greens(0.8), '#ffffff', plt.cm.Reds(0.8)])
norm = mcolors.Normalize(vmin=-0.5, vmax=0.5)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])

# Add colorbar
cbar = fig.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.046, pad=0.04)
cbar.set_label('Residuals: Actual - Expected Insecurity Ratio', fontsize=12)
cbar.set_ticks([-0.5, 0, 0.5])
cbar.set_ticklabels(['Negative Residuals\n(More Secure)', 'Zero Residuals\n(As Expected)', 'Positive Residuals\n(Less Secure)'])

plt.savefig('../figures/fig4_5_wealth_normalized_protocol.png')

# Calculate standard error of regression for significance testing
y_pred = model.predict(X)
residuals = y - y_pred
mse = np.mean(residuals**2)
std_error = np.sqrt(mse)

# Debug: Show residual distribution first
valid_residuals = data_with_wealth['insecurity_residual'].dropna()

# Use a more reasonable threshold: 1 standard deviation of the actual residuals
residual_std = valid_residuals.std()
significance_threshold = 1.0 * residual_std

# Find significantly deviating countries
significant_countries = data_with_wealth[
    (~data_with_wealth['insecurity_residual'].isna()) &
    (np.abs(data_with_wealth['insecurity_residual']) > significance_threshold)
].copy()

print(f"\nRegression Summary:")
print(f"R² = {model.score(X, y):.3f}")
print(f"Regression Standard Error = {std_error:.3f}")
print(f"Residual Standard Deviation = {residual_std:.3f}")
print(f"Significance Threshold (1.0 * residual_std) = {significance_threshold:.3f}")

print(f"Residual range: {valid_residuals.min():.3f} to {valid_residuals.max():.3f}")
print(f"Countries with negative residuals: {(valid_residuals < 0).sum()}")
print(f"Countries with positive residuals: {(valid_residuals > 0).sum()}")

print(f"\n=== Countries Significantly Deviating from Wealth-Expected Insecurity ===")
print(f"(Threshold: |residual| > {significance_threshold:.3f})")

if len(significant_countries) > 0:
    # Sort by absolute residual magnitude
    significant_countries = significant_countries.reindex(
        significant_countries['insecurity_residual'].abs().sort_values(ascending=False).index
    )

    print(f"\n🔴 WORSE than expected ({len(significant_countries[significant_countries['insecurity_residual'] > 0])} countries):")
    worse_countries = significant_countries[significant_countries['insecurity_residual'] > 0]
    for _, row in worse_countries.iterrows():
        starlink_secure = row['starlink_total'] - row['starlink_insecure']
        non_starlink_insecure = row['all_insecure'] - row['starlink_insecure']
        non_starlink_total = row['all_total'] - row['starlink_total']
        non_starlink_secure = non_starlink_total - non_starlink_insecure
        print(f"  {row['country_name']}: residual = {row['insecurity_residual']:.3f} (expected: {row['expected_insecurity']:.3f}, actual: {row['insecure_ratio']:.3f})")
        print(f"    Starlink: {int(row['starlink_insecure'])} insecure, {int(starlink_secure)} secure")
        print(f"    Non-Starlink: {int(non_starlink_insecure)} insecure, {int(non_starlink_secure)} secure")

    print(f"\n🟢 BETTER than expected ({len(significant_countries[significant_countries['insecurity_residual'] < 0])} countries):")
    better_countries = significant_countries[significant_countries['insecurity_residual'] < 0]
    for _, row in better_countries.iterrows():
        starlink_secure = row['starlink_total'] - row['starlink_insecure']
        non_starlink_insecure = row['all_insecure'] - row['starlink_insecure']
        non_starlink_total = row['all_total'] - row['starlink_total']
        non_starlink_secure = non_starlink_total - non_starlink_insecure
        print(f"  {row['country_name']}: residual = {row['insecurity_residual']:.3f} (expected: {row['expected_insecurity']:.3f}, actual: {row['insecure_ratio']:.3f})")
        print(f"    Starlink: {int(row['starlink_insecure'])} insecure, {int(starlink_secure)} secure")
        print(f"    Non-Starlink: {int(non_starlink_insecure)} insecure, {int(non_starlink_secure)} secure")

else:
    print("No countries significantly deviate from wealth-expected levels.")

# Show the most negative residuals for context
print(f"\n📊 Most negative residuals (green on map, but not significant):")
most_negative = data_with_wealth.nsmallest(5, 'insecurity_residual')[['country_name', 'insecurity_residual', 'expected_insecurity', 'insecure_ratio']]
for _, row in most_negative.iterrows():
    if not pd.isna(row['insecurity_residual']):
        print(f"  {row['country_name']}: residual = {row['insecurity_residual']:.3f} (expected: {row['expected_insecurity']:.3f}, actual: {row['insecure_ratio']:.3f})")

print(f"\nTotal countries analyzed: {len(regression_data)}")
print(f"Countries with significant deviations: {len(significant_countries)}")

data_with_wealth.to_html("../html/fig4_5_wealth_normalized_protocol.html")