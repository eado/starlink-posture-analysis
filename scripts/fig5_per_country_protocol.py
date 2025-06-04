import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = pd.read_csv("../data/raw/insecure_hosts/insecure_hosts.csv")
data["insecure_ratio"] = data["starlink_insecure_rate"] / data["all_insecure_rate"]
data = data.dropna()

top_10 = data.sort_values(by='insecure_ratio', ascending=False).head(10)
top_10['ratio'] = top_10['starlink_insecure_rate'] / top_10['all_insecure_rate'].replace(0, np.nan)
top_10['percent_more'] = (top_10['ratio'] - 1) * 100

# Plot as horizontal bars
fig, ax = plt.subplots(figsize=(8, 6))

y = range(len(top_10))

# Plot Starlink rates
ax.barh([i + 0.2 for i in y], top_10['starlink_insecure_rate'], color='red', height=0.4, label='Starlink Insecure Rate')

# Plot All rates
ax.barh([i - 0.2 for i in y], top_10['all_insecure_rate'], color='blue', height=0.4, label='All Insecure Rate')

# Annotate multiplicative difference on Starlink bars
for i, percent_more in enumerate(top_10['percent_more']):
    if not np.isnan(percent_more):
        ax.text(top_10['starlink_insecure_rate'].iloc[i]+0.003, i + 0.2, f"{percent_more:.0f}% more", 
                va='center', fontsize=10, color='darkred')

# Axis labels and title
ax.set_ylabel('Country')
ax.set_xlabel('Insecure Rate (%)')
ax.set_title('Top 10 Countries by Insecure Ratio (Starlink vs All)')

# Country labels on y-axis
ax.set_yticks(y)
ax.set_yticklabels(top_10['country_name'])

# Invert y-axis to show highest at top
ax.invert_yaxis()

# Legend
ax.legend(loc='lower right')

max_rate = top_10['starlink_insecure_rate'].max()
ax.set_xlim(0, max_rate * 1.2)

plt.tight_layout()
plt.savefig('../figures/fig5_per_country_protocol.png')
