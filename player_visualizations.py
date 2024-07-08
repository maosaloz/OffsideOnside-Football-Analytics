import json
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import os
from mplsoccer import VerticalPitch, FontManager
from mplsoccer import Pitch
from scipy.ndimage import gaussian_filter
from PIL import Image
import time
import numpy as np
import matplotlib
from matplotlib.colors import to_rgba
from matplotlib.colors import Normalize, LogNorm
import matplotlib.transforms as transforms
import warnings
warnings.filterwarnings("ignore")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import clipboard
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

import matplotlib.colors as mcolors

""" 
# Variables
data_download_loc = '/Users/Mao/Downloads'
chrome_driver_loc = '/Users/Mao/Downloads/chromedriver-mac-arm64/chromedriver'
url = 'https://www.whoscored.com/Matches/1735525/Live/Belgium-Jupiler-Pro-League-2023-2024-Union-St-Gilloise-Eupen'
match = 'Union St. Gilloise 4-1 Eupen'  # Modify with your match identifier

# Configure Selenium options
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": data_download_loc}
options.add_experimental_option("prefs", prefs)

# Start WebDriver session
s = Service(chrome_driver_loc)
driver = webdriver.Chrome(service=s, options=options)
driver.get(url)

# Wait for the page to load completely
time.sleep(10)

# Get page source
t = driver.page_source

# Extract team data
start_team_data = t.find("matchCentreData") + len('matchCentreData') + 2
end_team_data = t[t.find("matchCentreData"):].find('matchCentreEventTypeJson') + start_team_data - 30
team_data_output = t[start_team_data:end_team_data]

driver.close()

# Process team data
s = Service(chrome_driver_loc)
driver = webdriver.Chrome(service=s)
driver.get("https://konklone.io/json")
input_css = 'body > section.json > div.areas > textarea'
input_area = driver.find_element(by=By.CSS_SELECTOR, value=input_css)

# Copy team data to clipboard and paste it
clipboard.copy(team_data_output)
input_area.clear()
input_area.send_keys(Keys.SHIFT, Keys.INSERT)

# Click the download button for team data
click_css = 'body > section.csv > p > span.rendered > a.download'
driver.find_element(by=By.CSS_SELECTOR, value=click_css).click()
time.sleep(3)

driver.close()


os.chdir(data_download_loc)
files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
df_base = pd.read_csv(f'{data_download_loc}/{files[-1]}')
os.rename(f'{data_download_loc}/{files[-1]}', f'result {match}.csv')
"""

df_base = pd.read_csv(r'/Users/Mao/Downloads/result Union St. Gilloise 4-1 Eupen.csv') 

#df_base = df_base.loc[df_base['playerId'] == 134493]    # Add this to the function
    
    
matplotlib.rcParams['figure.dpi'] = 300

end_color_h = '#FF4500'                #!!!!! CHANGE THIS TO MATCH THE OFFSIDE/ONSIDE TEMPLATE !!!!!
end_color_a = '#D81B60'                # Add this to the function
kitline_h = '#a8d0f5'
kitline_a = '#f29aba'

name_h = 'Home' # Add to the function
name_a = 'Away' # Add to the function
    
URL = 'https://github.com/googlefonts/BevanFont/blob/main/fonts/ttf/Bevan-Regular.ttf?raw=true'
fprop = FontManager(URL).prop
    
player_id = 431791
player_name = 'Cameron Puertas'
    

################################################################################
# Pass map
################################################################################

# Initialize the pitch
pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')

# Create a figure and axis
fig, ax = pitch.draw(figsize=(10, 7))

# Plot the player's participation for 'Passes'
player_id = 431791
player_name = 'Cameron Puertas'
player_data = df_base[(df_base['playerId'] == player_id) & (df_base['type/displayName'] == 'Pass')]

#
# Separate successful and unsuccessful passes
successful_passes = player_data[player_data['outcomeType/displayName'] != 'Unsuccessful']
unsuccessful_passes = player_data[player_data['outcomeType/displayName'] == 'Unsuccessful']

# Plot start points of the passes
pitch.scatter(successful_passes['x'], successful_passes['y'], s=100, c='#1A78CF', edgecolors='#1A78CF', linewidth=1, alpha=0.7, ax=ax, label='Successful Passes')
pitch.scatter(unsuccessful_passes['x'], unsuccessful_passes['y'], s=100, c='#FF4500', edgecolors='#FF4500', linewidth=1, alpha=0.7, ax=ax, label='Unsuccessful Passes')

# Plot arrows for successful passes
pitch.arrows(successful_passes['x'], successful_passes['y'], successful_passes['endX'], successful_passes['endY'],
             color='#1A78CF', ax=ax, headwidth=5, headlength=5, headaxislength=5, width=3, alpha=0.7)

# Plot arrows for unsuccessful passes
pitch.arrows(unsuccessful_passes['x'], unsuccessful_passes['y'], unsuccessful_passes['endX'], unsuccessful_passes['endY'],
             color='#FF4500', ax=ax, headwidth=5, headlength=5, headaxislength=5, width=3, alpha=0.7)

title_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 30}
label_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 20}

ax.set_title(f"{player_name} - Passes", fontdict=title_font)
ax.set_xlabel('Direction ---->', fontdict=label_font)

# Add legend
ax.legend(loc='lower right', bbox_to_anchor=(1, -0.1))

plt.savefig(f"/Users/Mao/Downloads/{player_name}_Passes.png")

# Show the plot
plt.show()

################################################################################
# Heatmap 
################################################################################

pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2)
player_data = df_base[(df_base['playerId'] == player_id)]

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
ax.set_title(f"{player_name} - Heatmap", fontdict=title_font)
ax.set_xlabel('Direction ->', fontdict=label_font)
ax.set_ylabel('')

plt.savefig(f"/Users/Mao/Downloads/{player_name}_Heatmap.png")

# Show the plot
plt.show()

################################################################################
# Shotmap 
################################################################################

pitch = VerticalPitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')

# Create a figure and axis
fig, ax = plt.subplots(figsize=(7, 10))
pitch.draw(ax=ax)

shot_data = df_base[(df_base['type/displayName'] == 'MissedShots') | (df_base['type/displayName'] == 'SavedShot') |
                    (df_base['type/displayName'] == 'Goal') | (df_base['type/displayName'] == 'ShotOnPost')]
shot_data = shot_data[(shot_data['playerId'] == player_id)]

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

plt.savefig(f"/Users/Mao/Downloads/{player_name}_Shots.png")

# Show the plot
plt.show()