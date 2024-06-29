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
from matplotlib.colors import Normalize
import warnings
warnings.filterwarnings("ignore")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import clipboard
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

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

df_base = df_base.loc[df_base['playerId'] == 134493]    # Add this to the function
    
    
matplotlib.rcParams['figure.dpi'] = 300

end_color_h = '#1E88E5'                #!!!!! CHANGE THIS TO MATCH THE OFFSIDE/ONSIDE TEMPLATE !!!!!
end_color_a = '#D81B60'                # Add this to the function
kitline_h = '#a8d0f5'
kitline_a = '#f29aba'

name_h = 'Home' # Add to the function
name_a = 'Away' # Add to the function
    
URL = 'https://github.com/googlefonts/BevanFont/blob/main/fonts/ttf/Bevan-Regular.ttf?raw=true'
fprop = FontManager(URL).prop
    
    
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
df_base = df_base[df_base['period/displayName']!='PenaltyShootout'].reset_index(drop=True)

type_cols = [col for col in df_base.columns if '/type/displayName' in col]

df_base['endX'] = 0.0
df_base['endY'] = 0.0
for i in range(len(df_base)):
        df1 = df_base.iloc[i:i+1,:]
        j = 0
        for j in range(len(type_cols)):
            col = df1[type_cols[j]].values[0]
            if col == 'PassEndX':
                endx = df1.loc[:,'qualifiers/%i/value' %j].values[0]
                df_base['endX'][i] = float(endx)
            else:
                j +=1
        k = 0
        for k in range(len(type_cols)):
            col = df1[type_cols[k]].values[0]
            if col == 'PassEndY':
                endy = df1.loc[:,'qualifiers/%i/value' %k].values[0]
                df_base['endY'][i] = float(endy)
            else:
                k +=1

df_base['Cross'] = 0
for i in range(len(df_base)):
        df_base1 = df_base.iloc[i:i+1,:]
        j = 0
        for j in range(len(type_cols)):
            col = df_base1[type_cols[j]].values[0]
            if col == 'Cross':
                df_base['Cross'][i] = 1
            else:
                j +=1

df_base['Corner'] = 0
for i in range(len(df_base)):
        df_base1 = df_base.iloc[i:i+1,:]
        j = 0
        for j in range(len(type_cols)):
            col = df_base1[type_cols[j]].values[0]
            if col == 'CornerTaken':
                df_base['Corner'][i] = 1
            else:
                j +=1

df_base['KeyPass'] = 0
for i in range(len(df_base)):
        df_base1 = df_base.iloc[i:i+1,:]
        j = 0
        for j in range(len(type_cols)):
            col = df_base1[type_cols[j]].values[0]
            if col == 'KeyPass':
                df_base['KeyPass'][i] = 1
            else:
                j +=1

df_base['ShotAssist'] = 0
for i in range(len(df_base)):
        df_base1 = df_base.iloc[i:i+1,:]
        j = 0
        for j in range(len(type_cols)):
            col = df_base1[type_cols[j]].values[0]
            if col == 'ShotAssist':
                df_base['ShotAssist'][i] = 1
            else:
                j +=1

df_base['FK'] = 0
for i in range(len(df_base)):
        df_base1 = df_base.iloc[i:i+1,:]
        j = 0
        for j in range(len(type_cols)):
            col = df_base1[type_cols[j]].values[0]
            if col == 'FreeKickTaken':
                df_base['FK'][i] = 1
            else:
                j +=1
df_base['IFK'] = 0
for i in range(len(df_base)):
        df_base1 = df_base.iloc[i:i+1,:]
        j = 0
        for j in range(len(type_cols)):
            col = df_base1[type_cols[j]].values[0]
            if col == 'IndirectFreeKickTaken':
                df_base['IFK'][i] = 1
            else:
                j +=1
df_base['GK'] = 0
for i in range(len(df_base)):
        df_base1 = df_base.iloc[i:i+1,:]
        j = 0
        for j in range(len(type_cols)):
            col = df_base1[type_cols[j]].values[0]
            if col == 'GoalKick':
                df_base['GK'][i] = 1
            else:
                j +=1
df_base['ThrowIn'] = 0
for i in range(len(df_base)):
        df_base1 = df_base.iloc[i:i+1,:]
        j = 0
        for j in range(len(type_cols)):
            col = df_base1[type_cols[j]].values[0]
            if col == 'ThrowIn':
                df_base['ThrowIn'][i] = 1
            else:
                j +=1

df_base['GoalMouthY'] = 0.0
df_base['GoalMouthZ'] = 0.0
for i in range(len(df_base)):            
        df_base1 = df_base.iloc[i:i+1,:]
        j = 0
        for j in range(len(type_cols)):
            col = df_base1[type_cols[j]].values[0]
            if col == 'GoalMouthY':
                mouthy = df_base1.loc[:,'qualifiers/%i/value' %j].values[0]
                df_base['GoalMouthY'][i] = mouthy
            else:
                j +=1
        k = 0
        for k in range(len(type_cols)):
            col = df_base1[type_cols[k]].values[0]
            if col == 'GoalMouthZ':
                mouthz = df_base1.loc[:,'qualifiers/%i/value' %k].values[0]
                df_base['GoalMouthZ'][i] = mouthz
            else:
                k +=1
try:            
        for i in range(len(df_base)):
            tid = df_base.teamId[i]
            if df_base.isOwnGoal[i] == True:
                if tid == teamId_h:
                    df_base.teamId[i] = teamId_a
                    df_base.x[i] = 100-df_base.x[i]
                    df_base.y[i] = 100-df_base.y[i]
                elif tid == teamId_a:
                    df_base.teamId[i] = teamId_h
except:
        pass
    #####################

df_base['RedCard'] = 0
for i in range(len(df_base)):
        df_base1 = df_base.iloc[i:i+1,:]
        j = 0
        for j in range(len(type_cols)):
            col = df_base1[type_cols[j]].values[0]
            if col in ['SecondYellow','Red']:
                df_base['RedCard'][i] = 1
            else:
                j +=1
                
################################################################################
#                               Passing heat map setup                         #
################################################################################
                
                
df = df_base.copy()
df = df[(df['Corner']==0) & (df['FK']==0) & (df['IFK']==0) & (df['GK']==0) & (df['ThrowIn']==0)]
df = df[(df['type/displayName']=='Pass') & (df['outcomeType/value']==1)]

xT = pd.read_csv('https://raw.githubusercontent.com/mckayjohns/youtube-videos/main/data/xT_Grid.csv', header=None)
xT = np.array(xT)
xT_rows, xT_cols = xT.shape

df['x1_bin_xT'] = pd.cut(df['x'], bins=xT_cols, labels=False)
df['y1_bin_xT'] = pd.cut(df['y'], bins=xT_rows, labels=False)

df['start_zone_value_xT'] = df[['x1_bin_xT', 'y1_bin_xT']].apply(lambda x: xT[x[1]][x[0]], axis=1)

df['xT'] = df['end_zone_value_xT'] - df['start_zone_value_xT']

colors = np.arctan2(df['xT'],[.01]*len(df))

norm = Normalize()
norm.autoscale(colors)

################################################################################
#                               Passing heat map creation                      #
################################################################################

pitch = Pitch(pitch_type='opta', pitch_color='#FF4500', line_color='#F7FFFF', line_zorder=5, half=False)     
bins = (36, 19)

maxstat = pitch.bin_statistic(df.x, df.y,
                                 df.xT, statistic='sum', bins=bins,)
maxstatend = pitch.bin_statistic(df.endX, df.endY,
                                    df.xT, statistic='sum', bins=bins,)

dfh = df[df['playerId']==teamId_h].reset_index(drop=True)

pitch = Pitch(pitch_type='opta', pitch_color='#fbf9f4', line_color='#4A2E19', line_zorder=5, half=False)
fig, ax = pitch.draw(figsize=(6.276, 6.276/2))
fig.set_facecolor('#fbf9f4')

my_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#fbf9f4',end_color_h])
# blank_hmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#fbf9f4','#fbf9f4'])

bins = (36, 19)
bs_heatmap = pitch.bin_statistic(df[df['playerId']==teamId_h].x, df[df['playerId']==teamId_h].y,
                                  values=df[df['playerId']==teamId_h].xT, statistic='sum', bins=bins,)
bs_heatmap['statistic'] = gaussian_filter(bs_heatmap['statistic'], 1)

####################################################
# EDITING THE VISUALIZATION

hm = pitch.heatmap(bs_heatmap, ax=ax, cmap=my_cmap, edgecolor='#fbf9f4', vmin=0, lw=.1,
                    vmax=np.percentile(maxstat['statistic'],95)
                          )

ax.text(50, 102, "%s Passing Heatmap" %name_h,
                          color='#4A2E19',
                          va='bottom', ha='center',
                          fontproperties=fprop,
                          fontsize=22)

ax.text(50,-2, 'Direction of Attack --->',
                          color='#4A2E19',va='top', ha='center',
                          fontproperties=fprop,fontsize=13)

fig=plt.gcf()
fig.set_size_inches(6.276,6.276/2) #length, height
fig.patch.set_facecolor('#fbf9f4')

fig.savefig(f"{img_save_loc}/Home xT By Zone Start.png", dpi = 300)
plt.clf()