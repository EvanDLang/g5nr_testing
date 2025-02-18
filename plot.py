import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

to_highlight = [
    "1x4x67x480",
    "1x4x67x480", 
    "1x18x1x180x180",
    "1x6x67x480", 
    "1x4x67x180",
    "1x4x180x576",
    "1x4x67x640",
    "1x3x67x180",
    "1x2x91x180",
    "1x2x182x360",
    "1x2x121x192",
    "1x2x144x240"
]


directory = "experiments"
# Load the CSV data into a pandas DataFrame
df = pd.read_csv(os.path.join(directory, "chunk-size.csv"))

# Clean the 'filename' by removing the "chunked-" part
df['filename'] = df['filename'].str.replace('chunked-', '')

# Find the 'original' row for normalization
original_row = df[df['filename'] == 'original']

# Normalize the values by dividing by the value in the 'original' row for each column
open_values_normalized = df['open'] / original_row['open'].values[0]
vertical_mean_values_normalized = df['vertical_mean'] / original_row['vertical_mean'].values[0]
spatial_mean_values_normalized = df['spatial_mean'] / original_row['spatial_mean'].values[0]

# Prepare the data for plotting
labels = df['filename']

# Create the figure and axis for 3 subplots (adjusting height)
fig, axs = plt.subplots(2, 1, figsize=(14, 12))  # Reduced height

# Helper function to create the subplots
def create_subplot(ax, values, normalized_values, title, ylabel, add_legend=False):
    # Loop through the data and color bars based on whether chunk size is in the highlight list
    colors = ['orange' if label in to_highlight else 'b' for label in labels]
    
    # Create the bars with conditional coloring
    bars = ax.bar(labels, normalized_values, color=colors)
    
    ax.set_title(title, fontsize=14)
    ax.set_xlabel('Chunk Size', fontsize=12)  # Change x-axis label to "Chunk Size"
    ax.set_ylabel('')  # Drop the y-axis labels
    
    # Add the values on top of each bar (centered on the bars)
    for i in range(len(df)):
        ax.text(i, normalized_values[i] + 0.05, f'{normalized_values[i]:.2f}', ha='center', va='bottom', fontsize=8)

    # Rotate x-axis labels by 45 degrees to make them readable
    ax.tick_params(axis='x', rotation=45)

    # Set the y-axis limit to ensure all values and labels fit
    ax.set_ylim(0, max(normalized_values) * 1.2)  # Increase y limit by 20%

    # Add a legend to the first plot only
    if add_legend:
        orange_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='Decrease in File Size')
        ax.legend(handles=[orange_patch], loc='upper right')

# Create the subplots for each value
create_subplot(axs[0], df['vertical_mean'], vertical_mean_values_normalized, f'Vertical Mean Times vs Original', 'Normalized Seconds', add_legend=True)
create_subplot(axs[1], df['spatial_mean'], spatial_mean_values_normalized, f'Spatial Mean Times vs Original', 'Normalized Seconds', add_legend=False)
# create_subplot(axs[2], df['open'], open_values_normalized, f'Open Times vs Original', 'Normalized Seconds', add_legend=False)

# Adjust the layout to avoid overlap and save the plot
plt.tight_layout()
plt.savefig(os.path.join(directory, 'benchmarks.png'))
plt.close()
