import matplotlib.pyplot as plt
import seaborn as sns
import json


def load_and_process_data(file_path, replacements_list):
    """Loads and processes OS distribution data from a JSON file."""
    with open(file_path, 'r') as file:
        raw_data_list = json.load(file)

    processed_data_dict = dict()
    os_names_set = set()

    for data_row in raw_data_list:
        continent_name = data_row['continent']
        if continent_name not in processed_data_dict:
            processed_data_dict[continent_name] = dict()

        os_name_original = data_row['os']
        os_pretty_name = os_name_original.title()
        for old_str, new_str in replacements_list:
            os_pretty_name = os_pretty_name.replace(old_str, new_str)

        if os_pretty_name:
            processed_data_dict[continent_name][os_pretty_name] = float(data_row['percentage_share'])
            os_names_set.add(os_pretty_name)

    return processed_data_dict, os_names_set


def plot_continent_group_bars(ax_obj, group_data, y_offset, continents_order_list, colors_map, legend_os_set, bar_hgt):
    """Plots a group of stacked horizontal bars for OS distribution by continent."""
    current_group_y_ticks = []
    current_group_y_labels = []
    group_base_y = y_offset  # This is the y-value below the first bar's center of this group

    for idx, continent_val in enumerate(continents_order_list):
        # bar_center_y is the y-coordinate for the center of the horizontal bar
        bar_center_y = group_base_y + idx + 1
        current_group_y_ticks.append(bar_center_y)
        current_group_y_labels.append(continent_val)

        current_left_position = 0
        os_data_for_continent = group_data.get(continent_val, {})

        for os_key, percent_val in os_data_for_continent.items():
            bar_legend_label = None
            # Add to legend only if this OS hasn't been added before from any group
            if os_key not in legend_os_set:
                bar_legend_label = os_key
                legend_os_set.add(os_key)

            ax_obj.barh(bar_center_y, percent_val, left=current_left_position, height=bar_hgt,
                        color=colors_map.get(os_key), label=bar_legend_label)

            os_key_parts = os_key.split(" ")
            short_os_name_for_bar = " ".join(os_key_parts[1:]) if len(os_key_parts) > 1 else os_key
            if percent_val > 7:
                ax_obj.text(current_left_position + percent_val / 2, bar_center_y, short_os_name_for_bar,
                            ha='center', va='center', fontsize=9, fontweight='bold')
            current_left_position += percent_val

    # Return the y-coordinate of the center of the topmost bar in this group
    topmost_bar_center_y_in_group = group_base_y + len(continents_order_list)
    return current_group_y_ticks, current_group_y_labels, topmost_bar_center_y_in_group


# --- Configuration ---
json_file_path1 = '../data/raw/os_share_by_continent/bquxjob_4255453e_19630859374.json'
json_file_path2 = '../data/raw/os_share_by_continent/bquxjob_7e2fc6cf_196f5df2a7c.json'

os_name_replacements = [('os', 'OS'), ('Os', 'OS'), ('bsd', 'BSD'), ('MicrOSoft', 'Microsoft')]
# Order of continents for display (bottom to top for each group of bars)
continents_display_order = ['Oceania', 'South America', 'North America', 'Europe', 'Asia', 'Africa']

# --- Data Loading and Preparation ---
dataset1_data, dataset1_os_names = load_and_process_data(json_file_path1, os_name_replacements)
# It's assumed placeholder_second_file.json exists and has the same format.
dataset2_data, dataset2_os_names = load_and_process_data(json_file_path2, os_name_replacements)

combined_os_names = dataset1_os_names.union(dataset2_os_names)
num_unique_os = len(combined_os_names)
# Generate a color palette for all unique OS types across both datasets
color_palette = sns.color_palette("hls", num_unique_os)
os_color_mapping = dict(zip(combined_os_names, color_palette))

# --- Plotting Setup ---
num_continents_val = len(continents_display_order)
# Estimate figure height: 2 groups of bars, plus space for 2 headings and legend.
fig_height = (num_continents_val * 2 * 0.9) + 4
fig, ax = plt.subplots(figsize=(10, fig_height if fig_height > 10 else 12))

master_used_os_for_legend = set()
bar_element_height = 0.7
space_for_heading_and_padding = 1.5

# --- Plot Group 2 (Data from placeholder_second_file.json - BOTTOM group on chart) ---
ticks_for_group2, labels_for_group2, top_y_center_of_group2_bars = plot_continent_group_bars(
    ax, dataset2_data, 0, continents_display_order, os_color_mapping, master_used_os_for_legend, bar_element_height
)

y_pos_heading2 = top_y_center_of_group2_bars + (space_for_heading_and_padding / 2)
ax.text(50, y_pos_heading2, 'Non-Starlink Hosts', ha='center', va='center', fontsize=12, fontweight='bold')

# --- Plot Group 1 (Data from bquxjob_4255453e_19630859374.json - TOP group on chart) ---
y_offset_for_group1 = top_y_center_of_group2_bars + space_for_heading_and_padding
ticks_for_group1, labels_for_group1, top_y_center_of_group1_bars = plot_continent_group_bars(
    ax, dataset1_data, y_offset_for_group1, continents_display_order, os_color_mapping, master_used_os_for_legend,
    bar_element_height
)

y_pos_heading1 = top_y_center_of_group1_bars + (space_for_heading_and_padding / 2)
ax.text(50, y_pos_heading1, 'Starlink Hosts', ha='center', va='center', fontsize=12, fontweight='bold')

# --- Axes, Ticks, and Legend Configuration ---
combined_y_ticks = ticks_for_group2 + ticks_for_group1
combined_y_labels = labels_for_group2 + labels_for_group1

ax.set_yticks(combined_y_ticks)
ax.set_yticklabels(combined_y_labels)
ax.set_ylim(0, top_y_center_of_group1_bars + space_for_heading_and_padding)

ax.set_xlabel('Fraction of Hosts (%)')
ax.set_xlim(0, 100)

x_axis_percentage_ticks = [10, 20, 30, 40, 50, 60, 70, 80, 90]
ax.set_xticks(x_axis_percentage_ticks)
ax.set_xticklabels([f"{p}%" for p in x_axis_percentage_ticks])

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.tick_params(axis='y', which='both', length=0)
ax.tick_params(axis='x', which='both', length=0)

ax.xaxis.grid(True, linestyle='--', alpha=0.7)

handles, labels = ax.get_legend_handles_labels()
unique_legend_items = dict(zip(labels, handles))
ax.legend(unique_legend_items.values(), unique_legend_items.keys(),
          loc='upper center', bbox_to_anchor=(0.5, -0.06),
          fancybox=True, shadow=True, ncol=4)

plt.title('', fontsize=14, pad=20)
plt.tight_layout()
plt.subplots_adjust(bottom=0.15 if fig_height > 12 else 0.2)
plt.savefig('../figures/fig1_dist_exposed_os.png')
