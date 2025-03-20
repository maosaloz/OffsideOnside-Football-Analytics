# This code uses the visualizations we did for our Players to Watch article. It includes a pass map, heat map,
# shot map, progressive passes and defensive actions (Killian Sildilla). To run this code you'd need to adapt
# the following things, player_data path, player_name, logo_path, savefig path. The data is taken from the 
# player_webscrape code. 


import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mplsoccer.pitch import Pitch
import matplotlib.colors as mcolors
import matplotlib.image as mpimg
from scipy.ndimage import gaussian_filter
from mplsoccer import VerticalPitch, FontManager

player_data = pd.read_csv(r'/Users/Mao/Documents/Offside:onside/code/Olympics/Players to Watch/thiago_almada.csv') # adapt


player_name = 'Thiago Almada' # adapt
logo_path = '/Users/Mao/Downloads/offside_onside_logo.png' # adapt
logo = mpimg.imread(logo_path)
title_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 30}
label_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 20}
matplotlib.rcParams['figure.dpi'] = 300

################################################################################
# Pass map
################################################################################
# Initialize the pitch
pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')

# Create a figure and axis
fig, ax = pitch.draw(figsize=(10, 7))

# Plot the player's participation for 'Passes'
passes = player_data[(player_data['type/displayName'] == 'Pass')]

#
# Separate successful and unsuccessful passes
successful_passes = passes[passes['outcomeType/displayName'] != 'Unsuccessful']
unsuccessful_passes = passes[passes['outcomeType/displayName'] == 'Unsuccessful']

# Plot start points of the passes
pitch.scatter(successful_passes['x'], successful_passes['y'], s=100, c='#1A78CF', edgecolors='#1A78CF', linewidth=1, alpha=0.7, ax=ax, label='Successful Passes')
pitch.scatter(unsuccessful_passes['x'], unsuccessful_passes['y'], s=100, c='#FF4500', edgecolors='#FF4500', linewidth=1, alpha=0.7, ax=ax, label='Unsuccessful Passes')

# Plot arrows for successful passes
pitch.arrows(successful_passes['x'], successful_passes['y'], successful_passes['endX'], successful_passes['endY'],
             color='#1A78CF', ax=ax, headwidth=5, headlength=5, headaxislength=5, width=3, alpha=0.7)

# Plot arrows for unsuccessful passes
pitch.arrows(unsuccessful_passes['x'], unsuccessful_passes['y'], unsuccessful_passes['endX'], unsuccessful_passes['endY'],
             color='#FF4500', ax=ax, headwidth=5, headlength=5, headaxislength=5, width=3, alpha=0.7)


ax.set_title(f"{player_name}\nPasses", 
             fontdict=title_font,
             loc='left')
ax.set_xlabel('Direction --->', fontdict=label_font)

# Add legend
ax.legend(loc='lower right', bbox_to_anchor=(1, -0.1))

# Add the logo to the top right corner outside the pitch
newax = fig.add_axes([.77, .87, 0.13, 0.13], anchor='NE', zorder=1)
newax.imshow(logo)
newax.axis('off')

plt.savefig(f"/Users/Mao/Documents/Offside:onside/code/Olympics/Players to Watch/{player_name}_Passes.png") # adapt

# Show the plot
plt.show()

################################################################################
# Heatmap 
################################################################################

pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2)

# Create a figure and axis
fig, ax = pitch.draw(figsize=(10, 7))

# Define the bins for the heatmap
bins = (36, 19)

# Create the heatmap data
heatmap_data = pitch.bin_statistic(player_data['x'], player_data['y'], bins=bins, statistic='count')

# Apply a Gaussian filter to smooth the data
heatmap_data['statistic'] = gaussian_filter(heatmap_data['statistic'], sigma=2)

# Create a colormap ranging from transparent to #FF4500
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list('custom_orange', ['#F7FFFF', '#FF4500'])

# Plot the heatmap
pitch.heatmap(heatmap_data, ax=ax, cmap=cmap, edgecolors=None, alpha=0.8)

# Add title and labels
ax.set_title(f"{player_name}\nHeatmap", 
             fontdict=title_font,
             loc='left')
ax.set_xlabel('Direction --->', fontdict=label_font)
ax.set_ylabel('')

# Add the logo to the top right corner outside the pitch
newax = fig.add_axes([0.77, 0.87, 0.13, 0.13], anchor='NE', zorder=1)
newax.imshow(logo)
newax.axis('off')

plt.savefig(f"/Users/Mao/Documents/Offside:onside/code/Olympics/Players to Watch/{player_name}_Heatmap.png") # adapt

# Show the plot
plt.show()

################################################################################
# Shotmap 
################################################################################

pitch = VerticalPitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')

# Create a figure and axis
fig, ax = plt.subplots(figsize=(7, 10))
pitch.draw(ax=ax)

shot_data = player_data[(player_data['type/displayName'] == 'MissedShots') | (player_data['type/displayName'] == 'SavedShot') |
                    (player_data['type/displayName'] == 'Goal') | (player_data['type/displayName'] == 'ShotOnPost')]

goal = shot_data[shot_data['type/displayName'] == 'Goal']
post = shot_data[shot_data['type/displayName'] == 'ShotOnPost']
saved_shot = shot_data[shot_data['type/displayName'] == 'SavedShot']
missed_shots = shot_data[(shot_data['type/displayName'] == 'MissedShots')]

# Plot start points of the shots
pitch.scatter(goal['x'], goal['y'], s=100, c='#1A78CF', edgecolors='#1A78CF', linewidth=1, alpha=0.7, ax=ax, label='Goals')
pitch.scatter(post['x'], post['y'], s=100, c='#F7FFFF', edgecolors='#1A78CF', linewidth=1, alpha=1, ax=ax, label='Shots off the bar', marker='o')
pitch.scatter(saved_shot['x'], saved_shot['y'], s=100, c='#FF4500', edgecolors='#FF4500', linewidth=1, alpha=0.7, ax=ax, label='Saved shots')
pitch.scatter(missed_shots['x'], missed_shots['y'], s=100, c='#F7FFFF', edgecolors='#FF4500', linewidth=1, alpha=1, ax=ax, label='Missed shots', marker='o')


# Set the limits to show only the right half of the pitch
ax.set_xlim(0, 100)
ax.set_ylim(70, 100)

# Add title and labels with Charter font
title_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 20}
label_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 14}


ax.set_title(f"{player_name}\nShot Map", 
             fontdict=title_font, 
             loc='left', 
             pad=20)

# Add legend in the upper right, moved higher
ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.1), ncol=4)

# Add the logo to the top right corner outside the pitch
newax = fig.add_axes([0.8, 0.62, 0.1, 0.1], anchor='NE', zorder=1)
newax.imshow(logo)
newax.axis('off')

plt.savefig(f"/Users/Mao/Documents/Offside:onside/code/Olympics/Players to Watch/{player_name}_Shots.png", bbox_inches='tight') # adapt

# Show the plot
plt.show()

################################################################################
# progressive passes
################################################################################

comp_actions = player_data[(player_data['outcomeType/displayName'] == 'Successful') & player_data['endX'].notna() & 
                       player_data['endY'].notna()]

# Define a function to apply
def transform_endY(value):
    if value > 50:
        return 100 - value
    else:
        return value

# Create the new column using the custom function
comp_actions['temp_y'] = comp_actions['y'].apply(transform_endY)
comp_actions['temp_endY'] = comp_actions['endY'].apply(transform_endY)

def calculate_ratio(row):
    # Extract values from the row
    endX = row['endX']
    x = row['x']
    temp_endY = row['temp_endY']
    temp_y = row['temp_y']

    denominator = np.sqrt(x)
    numerator = ((endX - x) + (temp_endY - temp_y)) * (x)
    ratio = numerator/denominator
    return ratio

comp_actions['pp_ratio'] = comp_actions.apply(calculate_ratio, axis=1)
#comp_actions['pp_ratio'] = comp_actions[comp_actions['pp_ratio']>=0] # change if we want to include all passes

pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')

fig, ax = plt.subplots(figsize=(7, 10))
pitch.draw(ax=ax)

pitch_width = 100
pitch_height = 100

# Draw dotted lines every 20 units on x-axis
for x in range(0, pitch_width + 1, 20):
    ax.axvline(x, color='black', linestyle=':', linewidth=1)

# Draw dotted lines every 25 units on y-axis
for y in range(0, pitch_height + 1, 25):
    ax.axhline(y, color='black', linestyle=':', linewidth=1)

# Calculate min and max pp_ratio
min_ratio = comp_actions['pp_ratio'].min()
max_ratio = comp_actions['pp_ratio'].max()

# Normalize pp_ratio for overlay color
if min_ratio == max_ratio:
    comp_actions['normalized_ratio'] = 1
else:
    comp_actions['normalized_ratio'] = (comp_actions['pp_ratio'] - min_ratio) / (max_ratio - min_ratio)

# Drop rows where 'normalized_ratio' equals 0
comp_actions = comp_actions[comp_actions['normalized_ratio'] != 0]

# Calculate min and max pp_ratio
min_ratio = comp_actions['pp_ratio'].min()
max_ratio = comp_actions['pp_ratio'].max()

# Normalize pp_ratio for overlay color
if min_ratio == max_ratio:
    comp_actions['normalized_ratio'] = 1
else:
    comp_actions['normalized_ratio'] = (comp_actions['pp_ratio'] - min_ratio) / (max_ratio - min_ratio)

# Drop rows where 'normalized_ratio' equals 0
comp_actions = comp_actions[comp_actions['normalized_ratio'] != 0]

# Define pitch dimensions and grid
pitch_width = 100
pitch_height = 100
num_x_divisions = 5
num_y_divisions = 4

# Calculate grid dimensions
x_step = pitch_width / num_x_divisions
y_step = pitch_height / num_y_divisions

# Add a column for grid cell
def get_grid_cell(row):
    x_cell = int(row['x'] // x_step)
    y_cell = int(row['y'] // y_step)
    return f'cell_{x_cell}_{y_cell}'

comp_actions['grid_cell'] = comp_actions.apply(get_grid_cell, axis=1)

# Calculate the sum of normalized_ratio for each grid cell
grid_cell_sums = comp_actions.groupby('grid_cell')['normalized_ratio'].sum()

# Define the gradient color map (darker shades for higher values)
color_map = mcolors.LinearSegmentedColormap.from_list('orange_gradient', ['#FFFFFF', '#FFA500'])

# Initialize the pitch
pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')

fig, ax = plt.subplots(figsize=(7, 10))
pitch.draw(ax=ax)

# Draw dotted lines every 20 units on x-axis
for x in range(0, pitch_width + 1, 20):
    ax.axvline(x, color='black', linestyle=':', linewidth=1)

# Draw dotted lines every 25 units on y-axis
for y in range(0, pitch_height + 1, 25):
    ax.axhline(y, color='black', linestyle=':', linewidth=1)

# Normalize grid cell sums for color mapping
min_sum = grid_cell_sums.min()
max_sum = grid_cell_sums.max()

if min_sum == max_sum:
    min_sum = 0  # Avoid division by zero for normalization

# Draw the grid cells with appropriate gradient color
for cell, total_sum in grid_cell_sums.items():
    x_cell, y_cell = map(int, cell.split('_')[1:3])
    x_start = x_cell * x_step
    y_start = y_cell * y_step
    width = x_step
    height = y_step
    # Normalize the summed ratio for color mapping
    normalized_sum = (total_sum - min_sum) / (max_sum - min_sum)
    color = color_map(normalized_sum)
    rect = Rectangle((x_start, y_start), width, height, color=color, alpha=0.6)
    ax.add_patch(rect)

# Plot the data points and arrows with dynamic widths
comp_actions['arrow_width'] = comp_actions['normalized_ratio'] * 4  # Adjust the multiplier as needed for visibility

pitch.scatter(comp_actions['x'], comp_actions['y'], s=50, c='#808080', edgecolors='#808080', linewidth=1, alpha=0.7, ax=ax)

for _, row in comp_actions.iterrows():
    pitch.arrows(row['x'], row['y'], row['endX'], row['endY'],
                 color='#808080', ax=ax, headwidth=4, headlength=4, headaxislength=4,
                 width=row['arrow_width'], alpha=0.7)

# Set the limits to show the full pitch
ax.set_xlim(0, pitch_width)
ax.set_ylim(0, pitch_height)

# Add title and labels
title_font = {'family': 'serif', 'fontsize': 20}
ax.set_title(f"{player_name}\nPass Progression", fontdict=title_font, loc='left', pad=20)

notes = """
The following data was taken from Thiago Almada's last five home matches with Atlanta United which include
games against Toronto FC, Houston Dynamo FC, Charlotte FC, DC United and Minnesota United. In these five
games Almada played three times in a center attacking midfield role, once as a left wing and once as right 
forward. Calculations are made based on the distance traveled to the oppositions' goal, weighed by where 
the pass was initiated.
"""
fig.text(0.13, 0.33, notes, ha='left', va='top', fontsize=7)
# Add legend in the upper right, moved higher
#ax.legend(loc='lower left', bbox_to_anchor=(0.5, -0.1), ncol=4)

# Add the logo to the top right corner outside the pitch
newax = fig.add_axes([0.8, 0.67, 0.1, 0.1], anchor='NE', zorder=1)
newax.imshow(logo)
newax.axis('off')

plt.savefig(f"/Users/Mao/Documents/Offside:onside/code/Olympics/Players to Watch/{player_name}_progressive_passes.png", bbox_inches='tight') # adapt

# Show the plot
plt.show()

################################################################################
# defensive actions
################################################################################

# Initialize the pitch
pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')

# Create a figure and axis
fig, ax = pitch.draw(figsize=(10, 7))

# Define the list of desired actions
desired_actions = [
    'BallRecovery', 'Foul', 'Interception', 'Aerial', 'Tackle',
    'Clearance', 'BlockedPass', 'BallTouch', 'Save', 'Challenge'
]

# Filter the DataFrame to keep only the desired actions
player_data = player_data[player_data['type/displayName'].isin(desired_actions)]

ball_recovery = player_data[player_data['type/displayName'] == 'BallRecovery']
foul = player_data[player_data['type/displayName'] == 'Foul']
interception = player_data[player_data['type/displayName'] == 'Interception']
tackle = player_data[(player_data['type/displayName'] == ' Tackle')]
save = player_data[player_data['type/displayName'] == 'Save']
challenge = player_data[(player_data['type/displayName'] == 'Challenge')]

# Plot start points of the shots
pitch.scatter(ball_recovery['x'], ball_recovery['y'], s=100, c='#1A78CF', edgecolors='#1A78CF', linewidth=1, alpha=0.7, ax=ax, label='Ball Recoveries')
pitch.scatter(foul['x'], foul['y'], s=100, c='#F7FFFF', edgecolors='#1A78CF', linewidth=1, alpha=1, ax=ax, label='Fouls', marker='o')
pitch.scatter(interception['x'], interception['y'], s=100, c='#FF4500', edgecolors='#FF4500', linewidth=1, alpha=0.7, ax=ax, label='Interceptions')
pitch.scatter(tackle['x'], tackle['y'], s=100, c='#F7FFFF', edgecolors='#FF4500', linewidth=1, alpha=1, ax=ax, label='Tackles', marker='o')
pitch.scatter(save['x'], save['y'], s=100, c='#F7FFFF', edgecolors='#1A78CF', linewidth=1, alpha=1, ax=ax, label='Saves', marker='D')
pitch.scatter(challenge['x'], challenge['y'], s=100, c='#F7FFFF', edgecolors='#FF4500', linewidth=1, alpha=1, ax=ax, label='Challenge', marker='D')


# Set the limits to show only the right half of the pitch
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

# Add title and labels with Charter font
title_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 20}
label_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 14}

ax.set_title(f"{player_name}\nDefensive Actions", 
             fontdict=title_font, 
             loc='left', 
             pad=20)

# Add legend in the upper right, moved higher
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=3)

# Add the logo to the top right corner outside the pitch
newax = fig.add_axes([0.85, 0.9, 0.1, 0.1], anchor='NE', zorder=1)
newax.imshow(logo)
newax.axis('off')

plt.savefig(f"/Users/Mao/Documents/Offside:onside/code/Olympics/Players to Watch/{player_name}_defensive_actions.png", bbox_inches='tight') # adapt

# Show the plot
plt.show()