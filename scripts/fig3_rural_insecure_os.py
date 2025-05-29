import matplotlib.pyplot as plt
import numpy as np
import json
import sqlite3
from matplotlib.ticker import PercentFormatter
import seaborn as sns  # For KDE plot
from statsmodels.nonparametric.smoothers_lowess import lowess  # For LOESS

# --- Your existing code for data loading and preparation ---
starlink_data_file = '../data/raw/os_cve_locations/bquxjob_3c73f9c5_1965065a6b9.json'

with open(starlink_data_file, 'r') as file:
    starlink_raw_data = json.load(file)

data = list()

for entry in starlink_raw_data:
    formatted = dict()
    formatted['country_code'] = entry['country_code']
    formatted['percentage_with_cve'] = float(entry['percentage_with_cve'])
    data.append(formatted)


def get_rurality_by_a2(a2_value):
    try:
        database_path = "../data/raw/world_bank_rurality/wb_rurality.sqlite"
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        table_name = 'api_sprurtotlzs_ds2_en_csv_v2_21017'
        rurality_column = "2023"
        a2_column = "ne_10m_admin_0_countries_iso_a2"
        query = f'SELECT "{rurality_column}" FROM {table_name} WHERE "{a2_column}" = ? LIMIT 1'
        cursor.execute(query, (a2_value,))
        result = cursor.fetchone()

        conn.close()
        return float(result[0]) if result and result[0] is not None else None
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
    except ValueError as e:
        print(
            f"ValueError converting rurality: {e}. Value was: {result[0] if 'result' in locals() and result else 'N/A'}")
        return None


x_list = list()
y_list = list()
label_list = list()

for entry in data:
    rurality = get_rurality_by_a2(entry['country_code'])
    if rurality is None:
        continue

    if entry['percentage_with_cve'] <= 0:
        print(
            f"Skipping entry for {entry['country_code']} due to non-positive CVE percentage: {entry['percentage_with_cve']}")
        continue

    x_list.append(rurality)
    y_list.append(entry['percentage_with_cve'])
    label_list.append(entry['country_code'])

x_np = np.array(x_list)
y_np = np.array(y_list)

if len(x_np) == 0 or len(y_np) == 0:
    print("No data available to plot after filtering.")
    exit()

plt.figure(figsize=(3.5, 3))

if len(x_np) > 1 and len(y_np) > 1:
    sns.kdeplot(
        x=x_np,
        y=y_np,
        ax=plt.gca(),
        log_scale=(False, True),
        levels=5,
        color='orangered',  # Changed back to orangered
        fill=True,
        alpha=0.2,  # Kept alpha for filled area
        linewidths=0.5,
        zorder=1
    )

plt.scatter(x_np, y_np, color='blue', alpha=0.7, s=60, zorder=2)

if len(x_np) >= 5:
    y_log_for_loess = np.log10(y_np)
    sort_indices = np.argsort(x_np)
    x_sorted = x_np[sort_indices]
    y_log_sorted = y_log_for_loess[sort_indices]

    frac_loess = 2 / 3
    smoothed_data_log = lowess(y_log_sorted, x_sorted, frac=frac_loess, it=3)

    x_smooth = smoothed_data_log[:, 0]
    y_smooth_log = smoothed_data_log[:, 1]
    y_smooth = 10 ** y_smooth_log

    plt.plot(x_smooth, y_smooth, color='darkviolet', linewidth=1.75, linestyle='-', label='LOESS Trend',
             zorder=3)  # Changed LOESS to darkviolet for contrast

plt.xlabel('Rural Population Proportion', fontsize=9)
plt.ylabel('Fraction with OS CVE', fontsize=9)
plt.gca().xaxis.set_major_formatter(PercentFormatter(xmax=100))
plt.yscale('log')
plt.gca().yaxis.set_major_formatter(PercentFormatter(100))
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('../figures/fig3_rural_insecure_os.png')
