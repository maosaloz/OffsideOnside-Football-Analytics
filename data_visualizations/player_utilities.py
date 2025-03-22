#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 08:33:38 2025

@author: Mao
"""

import pandas as pd
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mplsoccer.pitch import Pitch
import matplotlib.colors as mcolors
import matplotlib.image as mpimg
from scipy.ndimage import gaussian_filter
from mplsoccer import VerticalPitch, FontManager

base_path = '/Users/Mao/Documents/Offside:onside'

logo_path = '/Users/Mao/Downloads/offside_onside_logo.png' # adapt
logo = mpimg.imread(logo_path)

title_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 30}
label_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 20}





def player_pass_map(data, player_name, league, gameweek): 
    pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')

    fig, ax = pitch.draw(figsize=(10, 7))
    
    data = data[data['player_name'] == player_name]
    passes = data[(data['action'] == 'Pass')] 

    successful_passes = passes[passes['outcome'] != 'Unsuccessful']   
    unsuccessful_passes = passes[passes['outcome'] == 'Unsuccessful']  

    pitch.scatter(successful_passes['x'], successful_passes['y'], s=100, c='#1A78CF', edgecolors='#1A78CF', linewidth=1, alpha=0.7, ax=ax, label='Successful Passes')
    pitch.scatter(unsuccessful_passes['x'], unsuccessful_passes['y'], s=100, c='#FF4500', edgecolors='#FF4500', linewidth=1, alpha=0.7, ax=ax, label='Unsuccessful Passes')
    
    pitch.arrows(successful_passes['x'], successful_passes['y'], successful_passes['endx'], successful_passes['endy'],
                 color='#1A78CF', ax=ax, headwidth=5, headlength=5, headaxislength=5, width=3, alpha=0.7)

    pitch.arrows(unsuccessful_passes['x'], unsuccessful_passes['y'], unsuccessful_passes['endx'], unsuccessful_passes['endy'],
                 color='#FF4500', ax=ax, headwidth=5, headlength=5, headaxislength=5, width=3, alpha=0.7)

    ax.set_title(f"{player_name}\nPasses", 
                 fontdict=title_font,
                 loc='left')
    ax.set_xlabel('Direction --->', fontdict=label_font)

    ax.legend(loc='lower right', bbox_to_anchor=(1, -0.1))

    newax = fig.add_axes([.77, .87, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    plt.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{player_name}_Passes.png"),
        dpi=300) 

    plt.show()
    


    
    
    
def player_heat_map(data, player_name, league, gameweek):
    
    pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2)

    fig, ax = pitch.draw(figsize=(10, 7))

    bins = (36, 19)

    data = data[data['player_name'] == player_name]
    heatmap_data = pitch.bin_statistic(data['x'], data['y'], bins=bins, statistic='count')

    heatmap_data['statistic'] = gaussian_filter(heatmap_data['statistic'], sigma=2)

    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list('custom_orange', ['#F7FFFF', '#FF4500'])

    pitch.heatmap(heatmap_data, ax=ax, cmap=cmap, edgecolors=None, alpha=0.8)

    ax.set_title(f"{player_name}\nHeatmap", 
                 fontdict=title_font,
                 loc='left')
    ax.set_xlabel('Direction --->', fontdict=label_font)
    ax.set_ylabel('')

    newax = fig.add_axes([0.77, 0.87, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    plt.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{player_name}_heat_map.png"),
        dpi=300)

    plt.show()






def player_shot_map(data, player_name, league, gameweek):
    
    pitch = VerticalPitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')

    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)
    
    data = data[data['player_name'] == player_name]

    shot_data = data[(data['action'] == 'MissedShots') | (data['action'] == 'SavedShot') |
                            (data['action'] == 'Goal') | (data['action'] == 'ShotOnPost')]

    goal = shot_data[shot_data['action'] == 'Goal']
    post = shot_data[shot_data['action'] == 'ShotOnPost']
    saved_shot = shot_data[shot_data['action'] == 'SavedShot']
    missed_shots = shot_data[(shot_data['action'] == 'MissedShots')]
    
    pitch.scatter(goal['x'], goal['y'], s=100, c='#1A78CF', edgecolors='#1A78CF', linewidth=1, alpha=0.7, ax=ax, label='Goals')
    pitch.scatter(post['x'], post['y'], s=100, c='#F7FFFF', edgecolors='#1A78CF', linewidth=1, alpha=1, ax=ax, label='Shots off the bar', marker='o')
    pitch.scatter(saved_shot['x'], saved_shot['y'], s=100, c='#FF4500', edgecolors='#FF4500', linewidth=1, alpha=0.7, ax=ax, label='Saved shots')
    pitch.scatter(missed_shots['x'], missed_shots['y'], s=100, c='#F7FFFF', edgecolors='#FF4500', linewidth=1, alpha=1, ax=ax, label='Missed shots', marker='o')

    ax.set_xlim(0, 100)
    ax.set_ylim(70, 100)
    
    title_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 20}
    label_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 14}


    ax.set_title(f"{player_name}\nShot Map", 
                 fontdict=title_font, 
                 loc='left', 
                 pad=20)

    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.1), ncol=4)
    
    newax = fig.add_axes([0.8, 0.62, 0.1, 0.1], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    plt.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{player_name}_shot_map.png"),
        dpi=300)

    plt.show()
    





def player_progressive_passes(data, player_name, notes, league, gameweek): 
    
    comp_actions = data[(data['outcome'] == 'Successful') & data['endx'].notna() & 
                       data['endy'].notna()]

    def transform_endY(value):
        if value > 50:
            return 100 - value
        else:
            return value

    comp_actions['temp_y'] = comp_actions['y'].apply(transform_endY)
    comp_actions['temp_endY'] = comp_actions['endy'].apply(transform_endY)

    def calculate_ratio(row):
                                                                                    # Extract values from the row
        endX = row['endx']
        x = row['x']
        temp_endY = row['temp_endY']
        temp_y = row['temp_y']
        
        denominator = np.sqrt(x)
        numerator = ((endX - x) + (temp_endY - temp_y)) * (x)
        ratio = numerator/denominator
        return ratio

    comp_actions['pp_ratio'] = comp_actions.apply(calculate_ratio, axis=1)
    #comp_actions['pp_ratio'] = comp_actions[comp_actions['pp_ratio']>=0]           # change if we want to include all passes

    pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')

    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)
    
    pitch_width = 100                                                               # Defining pitch dimensions and grid
    pitch_height = 100
    num_x_divisions = 5
    num_y_divisions = 4
    
    for x in range(0, pitch_width + 1, 20):                                         # Draw dotted lines every 20 units on x-axis
        ax.axvline(x, color='black', linestyle=':', linewidth=1)

    for y in range(0, pitch_height + 1, 25):                                        # Draw dotted lines every 25 units on y-axis
        ax.axhline(y, color='black', linestyle=':', linewidth=1)

    min_ratio = comp_actions['pp_ratio'].min()                                       # Calculate min and max pp_ratio
    max_ratio = comp_actions['pp_ratio'].max()

    if min_ratio == max_ratio:                                                      # Normalize pp_ratio for overlay color
        comp_actions['normalized_ratio'] = 1
    else:
        comp_actions['normalized_ratio'] = (comp_actions['pp_ratio'] - min_ratio) / (max_ratio - min_ratio)

    comp_actions = comp_actions[comp_actions['normalized_ratio'] != 0]              # Drop rows where 'normalized_ratio' equals 0

    x_step = pitch_width / num_x_divisions                                          # Calculate grid dimensions
    y_step = pitch_height / num_y_divisions

    def get_grid_cell(row):                                                         # Adding a column for grid cells
        x_cell = int(row['x'] // x_step)
        y_cell = int(row['y'] // y_step)
        return f'cell_{x_cell}_{y_cell}'

    comp_actions['grid_cell'] = comp_actions.apply(get_grid_cell, axis=1)

    grid_cell_sums = comp_actions.groupby('grid_cell')['normalized_ratio'].sum()

    color_map = mcolors.LinearSegmentedColormap.from_list('orange_gradient', ['#FFFFFF', '#FFA500'])

    pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')

    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)

    for x in range(0, pitch_width + 1, 20):                                         # Draw dotted lines every 20 units on x-axis
        ax.axvline(x, color='black', linestyle=':', linewidth=1)

    for y in range(0, pitch_height + 1, 25):                                        # Draw dotted lines every 25 units on y-axis
        ax.axhline(y, color='black', linestyle=':', linewidth=1)

    min_sum = grid_cell_sums.min()                                                  # Normalize grid cell sums for color mapping
    max_sum = grid_cell_sums.max()
    
    if min_sum == max_sum:                                                          # Avoid division by zero for normalization
        min_sum = 0                                         

    for cell, total_sum in grid_cell_sums.items():                                  # Draw the grid cells with appropriate gradient color
        x_cell, y_cell = map(int, cell.split('_')[1:3])
        x_start = x_cell * x_step
        y_start = y_cell * y_step
        width = x_step
        height = y_step
        normalized_sum = (total_sum - min_sum) / (max_sum - min_sum)                # Normalize the summed ratio for color mapping
        color = color_map(normalized_sum)
        rect = Rectangle((x_start, y_start), width, height, color=color, alpha=0.6)
        ax.add_patch(rect)
                                                                                    # Plot the data points and arrows with dynamic widths
    comp_actions['arrow_width'] = comp_actions['normalized_ratio'] * 4              # Adjust the multiplier as needed for visibility

    pitch.scatter(comp_actions['x'], comp_actions['y'], s=50, c='#808080', edgecolors='#808080', linewidth=1, alpha=0.7, ax=ax)

    for _, row in comp_actions.iterrows():
        pitch.arrows(row['x'], row['y'], row['endx'], row['endy'],
                     color='#808080', ax=ax, headwidth=4, headlength=4, headaxislength=4,
                     width=row['arrow_width'], alpha=0.7)

    ax.set_xlim(0, pitch_width)
    ax.set_ylim(0, pitch_height)

    title_font = {'family': 'serif', 'fontsize': 20}
    ax.set_title(f"{player_name}\nPass Progression", fontdict=title_font, loc='left', pad=20)

    notes = f"""{notes}"""
    fig.text(0.13, 0.12, notes, ha='left', va='top', fontsize=12)
    # Add legend in the upper right, moved higher
    #ax.legend(loc='lower left', bbox_to_anchor=(0.5, -0.1), ncol=4)

    newax = fig.add_axes([0.8, 0.88, 0.1, 0.1], anchor='NE', zorder=1)              # Add the logo to the top right corner outside the pitch
    newax.imshow(logo)
    newax.axis('off')

    plt.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{player_name}_progressive_passes.png"),
        dpi=300)
   
    plt.show()
    
    
    

def player_defensive_actions(data, player_name, league, gameweek): 
    
    pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')

    fig, ax = pitch.draw(figsize=(10, 7))

    desired_actions = [
        'BallRecovery', 'Foul', 'Interception', 'Aerial', 'Tackle',
        'Clearance', 'BlockedPass', 'BallTouch', 'Save', 'Challenge'
        ]

    player_data = data[data['action'].isin(desired_actions)]

    ball_recovery = player_data[player_data['action'] == 'BallRecovery']
    foul = player_data[player_data['action'] == 'Foul']
    interception = player_data[player_data['action'] == 'Interception']
    tackle = player_data[(player_data['action'] == ' Tackle')]
    save = player_data[player_data['action'] == 'Save']
    challenge = player_data[(player_data['action'] == 'Challenge')]

    pitch.scatter(ball_recovery['x'], ball_recovery['y'], s=100, c='#1A78CF', edgecolors='#1A78CF', linewidth=1, alpha=0.7, ax=ax, label='Ball Recoveries')
    pitch.scatter(foul['x'], foul['y'], s=100, c='#F7FFFF', edgecolors='#1A78CF', linewidth=1, alpha=1, ax=ax, label='Fouls', marker='o')
    pitch.scatter(interception['x'], interception['y'], s=100, c='#FF4500', edgecolors='#FF4500', linewidth=1, alpha=0.7, ax=ax, label='Interceptions')
    pitch.scatter(tackle['x'], tackle['y'], s=100, c='#F7FFFF', edgecolors='#FF4500', linewidth=1, alpha=1, ax=ax, label='Tackles', marker='o')
    pitch.scatter(save['x'], save['y'], s=100, c='#F7FFFF', edgecolors='#1A78CF', linewidth=1, alpha=1, ax=ax, label='Saves', marker='D')
    pitch.scatter(challenge['x'], challenge['y'], s=100, c='#F7FFFF', edgecolors='#FF4500', linewidth=1, alpha=1, ax=ax, label='Challenge', marker='D')

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    title_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 20}
    label_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 14}
    
    ax.set_title(f"{player_name}\nDefensive Actions", 
                 fontdict=title_font, 
                 loc='left', 
                 pad=40)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=3)
    
    newax = fig.add_axes([0.85, 0.9, 0.1, 0.1], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')
    
    plt.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{player_name}_defensive_actions.png"),
        dpi=300)
    
    plt.show()