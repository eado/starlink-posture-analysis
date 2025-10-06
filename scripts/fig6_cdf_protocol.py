import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats import norm as n, fisher_exact

data = pd.read_csv("../data/raw/insecure_hosts/insecure_hosts.csv")
data["insecure_ratio"] = data["starlink_insecure_rate"] / data["all_insecure_rate"]
data = data.dropna()

def compare_proportions(df):
    results = []

    for idx, row in df.iterrows():
        x1 = int(row['starlink_insecure'])
        n1 = int(row['starlink_total'])
        x2 = int(row['all_insecure'])
        n2 = int(row['all_total'])

        if n1 < 30:
            # Use Fisher's Exact Test (right-tailed)
            table = [[x1, n1 - x1],
                     [x2, n2 - x2]]
            _, pval = fisher_exact(table, alternative='greater')
            z_stat = np.nan
            test_used = "fisher"
        else:
            # One-tailed z-test (Starlink > All)
            p1 = x1 / n1
            p2 = x2 / n2
            p_pool = (x1 + x2) / (n1 + n2)
            se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))

            if se == 0:
                z_stat = np.nan
                pval = 1.0
            else:
                z_stat = (p1 - p2) / se
                pval = 1 - n.cdf(z_stat)  # One-tailed

            test_used = "z"

        results.append({
            'z_stat': z_stat,
            'p_value': pval,
            'test_used': test_used
        })

    return pd.concat([df, pd.DataFrame(results)], axis=1)

data = compare_proportions(data)

# Drop missing values (e.g., from Fisher's test if z_stat is nan)
p_values = data['p_value'].dropna().sort_values().values
print(data[data['p_value'] < 0.05])

# Compute empirical CDF
cdf_y = np.arange(1, len(p_values)+1) / len(p_values)

# Plot
plt.figure(figsize=(8, 5))
plt.plot(p_values, cdf_y, marker='o', linestyle='-', color='blue')
plt.title('CDF of P-values')
plt.xlabel('P-value')
plt.ylabel('Cumulative Probability')
plt.grid(True)
plt.axhline(0.95, color='red', linestyle='--', label='95%')
plt.axvline(0.05, color='green', linestyle='--', label='p=0.05')
plt.legend()
plt.savefig('../figures/fig6_cve_protocol.png')