# This code uses the Thiago Almada example from the Players to Watch article. The code scrapes on a game to game 
# basis therefore we should find a way to improve this codes efficiency. There are multiple things to adapt such as 
# player_id, player_name, data_download_loc, chrome_driver_loc (need to dowload chromedriver), url, match and lastly 
# the data at the end of the code. 

import pandas as pd
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.image as mpimg
import json
import os
import re
import time
import warnings
warnings.filterwarnings("ignore")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import clipboard
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service



player_id = 361732 # adapt
player_name = 'Thiago Almada' # adapth
player_data = pd.DataFrame()

data_download_loc = '/Users/Mao/Downloads' # adapt
chrome_driver_loc = '/Users/Mao/Downloads/chromedriver-mac-arm64 2/chromedriver' 

###########################################################################
# Atlanta United 2-1 Toronto

# Variables
url = 'https://www.whoscored.com/Matches/1791225/Live/USA-Major-League-Soccer-2024-Atlanta-United-Toronto-FC' #adapt
match = 'Atlanta United 2-1 Toronto'  # adapt

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

start_playerid = team_data_output.find('"playerIdNameDictionary":') + len('"playerIdNameDictionary":')
end_playerid = team_data_output.find(',"periodMinuteLimits"')  # Find the end of the dictionary
player_dict_str = team_data_output[start_playerid:end_playerid]

player_dict = json.loads(player_dict_str)
player_dict = {int(k): v for k, v in player_dict.items()}

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

os.chdir(data_download_loc)
files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
df_base = pd.read_csv(f'{data_download_loc}/{files[-1]}')  

df_base["playerId"] = df_base["playerId"].astype('Int64')  # Ensures proper integer type
df_base["playerName"] = df_base["playerId"].map(player_dict)

ft_score_match = re.search(r'"ftScore":"(.*?)"', team_data_output)
ft_score = ft_score_match.group(1) if ft_score_match else None

df_base["score"] = ft_score

home_teamid_match = re.search(r'"home":\{"teamId":(\d+)', team_data_output)
home_teamid = int(home_teamid_match.group(1)) if home_teamid_match else None  # Extract home teamId

df_base["home_teamid"] = home_teamid

#df_base = df_base[(df_base['playerId'] == player_id)]

#player_data = pd.concat([player_data ,df_base])

"""
###########################################################################
# DC United 0-1 Atlanta United

# Variables
data_download_loc = '/Users/Mao/Downloads'
chrome_driver_loc = '/Users/Mao/Downloads/chromedriver-mac-arm64/chromedriver'
url = 'https://www.whoscored.com/Matches/1791032/Live/USA-Major-League-Soccer-2024-DC-United-Atlanta-United'
match = 'DC United 0-1 Atlanta United'  # Modify with your match identifier

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

player_data = df_base[(df_base['playerId'] == player_id)]

player_data = pd.concat([player_data ,df_base])

###########################################################################
# Atlanta United 2-2 Houston

# Variables
url = 'https://www.whoscored.com/Matches/1790925/Live/USA-Major-League-Soccer-2024-Atlanta-United-Houston-Dynamo-FC' # adapt
match = 'Atlanta United 2-2 Houston'  # adapt

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

df_base = df_base[(df_base['playerId'] == player_id)]
player_data = pd.concat([player_data ,df_base])


###########################################################################
# Atlanta United 2-3 Charlotte FC

# Variables
url = 'https://www.whoscored.com/Matches/1790920/Live/USA-Major-League-Soccer-2024-Atlanta-United-Charlotte-FC' # adapt
match = 'Atlanta United 2-3 Charlotte FC'  # adapt

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

df_base = df_base[(df_base['playerId'] == player_id)]
player_data = pd.concat([player_data ,df_base])



###########################################################################
# Inter Miami 1-3 Atlanta United

# Variables
data_download_loc = '/Users/Mao/Downloads'
chrome_driver_loc = '/Users/Mao/Downloads/chromedriver-mac-arm64/chromedriver'
url = 'https://www.whoscored.com/Matches/1790939/Live/USA-Major-League-Soccer-2024-Inter-Miami-CF-Atlanta-United'
match = 'Inter Miami 1-3 Atlanta United'  # Modify with your match identifier

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

player_data = df_base[(df_base['playerId'] == player_id)]

player_data = pd.concat([player_data ,df_base])

player_data.to_csv(r'/Users/Mao/Documents/Offside:onside/code/Olympics/thiago_almada.csv', index=False)


###########################################################################
# Atlanta United 2-3 DC United

# Variables
url = 'https://www.whoscored.com/Matches/1790871/Live/USA-Major-League-Soccer-2024-Atlanta-United-DC-United' # adapt
match = 'Atlanta United 2-3 DC United'  # adapt

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

df_base = df_base[(df_base['playerId'] == player_id)]
player_data = pd.concat([player_data ,df_base])

###########################################################################
# Atlanta United 1-2 Minnesota United

# Variables
url = 'https://www.whoscored.com/Matches/1790844/Live/USA-Major-League-Soccer-2024-Atlanta-United-Minnesota-United' # adapt
match = 'Atlanta United 1-2 Minnesota United'  # adapt

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

df_base = df_base[(df_base['playerId'] == player_id)]
player_data = pd.concat([player_data ,df_base])
player_data.to_csv(r'/Users/Mao/Documents/Offside:onside/code/Olympics/Players to Watch/thiago_almada.csv', index=False) # adapt



###########################################################################
# Chicago 0-0 Atlanta United

# Variables
data_download_loc = '/Users/Mao/Downloads'
chrome_driver_loc = '/Users/Mao/Downloads/chromedriver-mac-arm64/chromedriver'
url = 'https://www.whoscored.com/Matches/1790838/Live/USA-Major-League-Soccer-2024-Chicago-Fire-FC-Atlanta-United'
match = 'Chicago 0-0 Atlanta United'  # Modify with your match identifier

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

player_data = df_base[(df_base['playerId'] == player_id)]

player_data = pd.concat([player_data ,df_base])


###########################################################################
# Atlanta United 1-2 FC Cincinnati

# Variables
data_download_loc = '/Users/Mao/Downloads'
chrome_driver_loc = '/Users/Mao/Downloads/chromedriver-mac-arm64/chromedriver'
url = 'https://www.whoscored.com/Matches/1790891/Live/USA-Major-League-Soccer-2024-Atlanta-United-FC-Cincinnati'
match = 'Atlanta United 1-2 FC Cincinnati'  # Modify with your match identifier

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

player_data = df_base[(df_base['playerId'] == player_id)]
player_data = pd.concat([player_data ,df_base])


###########################################################################
# Atlanta United 2-2 Philadelphia

# Variables
data_download_loc = '/Users/Mao/Downloads'
chrome_driver_loc = '/Users/Mao/Downloads/chromedriver-mac-arm64/chromedriver'
url = 'https://www.whoscored.com/Matches/1790887/Live/USA-Major-League-Soccer-2024-Atlanta-United-Philadelphia-Union'
match = 'Atlanta United 2-2 Philadelphia'  # Modify with your match identifier

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

player_data = df_base[(df_base['playerId'] == player_id)]
player_data = pd.concat([player_data ,df_base])

player_data.to_csv(r'/Users/Mao/Documents/Offside:onside/code/Olympics/thiago_almada.csv', index=False)



###########################################################################
# New York City FC 1-1 Atlanta United

# Variables
data_download_loc = '/Users/Mao/Downloads'
chrome_driver_loc = '/Users/Mao/Downloads/chromedriver-mac-arm64/chromedriver'
url = 'https://www.whoscored.com/Matches/1790764/Live/USA-Major-League-Soccer-2024-New-York-City-FC-Atlanta-United'
match = 'New York City FC 1-1 Atlanta United'  # Modify with your match identifier

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

player_data = df_base[(df_base['playerId'] == player_id)]
player_data = pd.concat([player_data ,df_base])
"""
