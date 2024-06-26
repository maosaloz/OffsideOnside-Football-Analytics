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

df_base = df_base.loc[df_base['playerId'] == 134493]
