#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 16 22:23:45 2025

@author: Mao
"""

# packages needed 
import pandas as pd
import numpy as np
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
from utilities import all_teams, serieA_teams, leagues, create_table_whoscored, data_download_loc, chrome_driver_loc


for team, team_id in serieA_teams.items():                                      # need to change this

    urls = []
    data = pd.DataFrame()
    
    league = leagues[team]
    print(f"Team: {team}, League: {league}")
    
    # getting match urls from the base url
    if league == 'ita_serie_a':
        base_url = f'https://www.whoscored.com/teams/{team_id}/fixtures/italy-{team}'
    elif league == 'la_liga':
        base_url = f'https://www.whoscored.com/teams/{team_id}/fixtures/spain-{team}'
    elif league == 'bundesliga':
        base_url = f'https://www.whoscored.com/teams/{team_id}/fixtures/germany-{team}'
    elif league == 'premier_league':
        base_url = f'https://www.whoscored.com/teams/{team_id}/fixtures/england-{team}'
    elif league == 'ligue1':
        base_url = f'https://www.whoscored.com/teams/{team_id}/fixtures/france-{team}'
    
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": data_download_loc}
    options.add_experimental_option("prefs", prefs)

    s = Service(chrome_driver_loc)
    driver = webdriver.Chrome(service=s, options=options)
    driver.get(base_url)

    time.sleep(20)
    
    agree = driver.find_element(By.XPATH, "//div[@class='Frame-buoy__sc-1d4hofp-0 fSVQFz']/button").click()
    
    div_path = driver.find_element(By.XPATH, "//div[@id='team-fixtures']/div")      # finding the path to the match urls
    child_divs = div_path.find_elements(By.XPATH, "./div")
    for div in child_divs:
        url_element = div.find_element(By.XPATH, "./div[9]/a")
        url = url_element.get_attribute("href")
        link_text = url_element.text.strip()
        
        if link_text.lower() !="vs":                                                # removing matches that haven't been played yet
            urls.append(url)
        else:
            print("Skipping URL")
    
    driver.close()
    
    for url in urls: 
    
        try:
            options = webdriver.ChromeOptions()                                             # webscraping data from whoscored
            prefs = {"download.default_directory": data_download_loc}
            options.add_experimental_option("prefs", prefs)
            
            s = Service(chrome_driver_loc)  
            driver = webdriver.Chrome(service=s, options=options)
            driver.get(url)

            time.sleep(20)

            t = driver.page_source

            start_team_data = t.find("matchCentreData") + len('matchCentreData') + 2        # Extracting json data
            end_team_data = t[t.find("matchCentreData"):].find('matchCentreEventTypeJson') + start_team_data - 30
            team_data_output = t[start_team_data:end_team_data]
                                                                                            # Extracting player id to name dictionary
            start_playerid = team_data_output.find('"playerIdNameDictionary":') + len('"playerIdNameDictionary":')
            end_playerid = team_data_output.find(',"periodMinuteLimits"')  
            player_dict_str = team_data_output[start_playerid:end_playerid]

            player_dict = json.loads(player_dict_str)
            player_dict = {int(k): v for k, v in player_dict.items()}                       # Making the playerid into an integer since it's an integer in the df dataframe

            driver.close()

            s = Service(chrome_driver_loc)                                                  # converting json to a dataframe using https://konklone.io/json
            driver = webdriver.Chrome(service=s)
            driver.get("https://konklone.io/json")
            
            input_css = 'body > section.json > div.areas > textarea'
        
            try:
                input_area = driver.find_element(by=By.CSS_SELECTOR, value=input_css)
                clipboard.copy(team_data_output)  
                input_area.clear()
                input_area.send_keys(Keys.SHIFT, Keys.INSERT)

                click_css = 'body > section.csv > p > span.rendered > a.download'  
                driver.find_element(by=By.CSS_SELECTOR, value=click_css).click()
                time.sleep(3)

            except (ElementNotInteractableException, NoSuchElementException, TimeoutException) as e:
                print(f"Skipping {url} due to element interaction issue: {e}")
                driver.close()
                continue  

            driver.close()

            os.chdir(data_download_loc)  
            files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
            df = pd.read_csv(f'{data_download_loc}/{files[-1]}')
                                                                                
            df["playerId"] = df["playerId"].astype('Int64')                         # Adding player name
            df["player_name"] = df["playerId"].map(player_dict)
            
            ft_score_match = re.search(r'"ftScore":"(.*?)"', team_data_output)      # Adding match score
            ft_score = ft_score_match.group(1) if ft_score_match else None

            df["score"] = ft_score

            home_teamid_match = re.search(r'"home":\{"teamId":(\d+)', team_data_output)     # Adding home teamid specification
            home_teamid = int(home_teamid_match.group(1)) if home_teamid_match else None  

            df["home_teamid"] = home_teamid

            unique_teams = df['teamId'].unique()                                    # Adding opponent specification
            if len(unique_teams) == 2:
                team_a, team_b = unique_teams
                df["opponentid"] = df["teamId"].map({team_a: team_b, team_b: team_a})

            data = pd.concat([data, df])

        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue  
    
    team_id_to_name = {int(v): k for k, v in all_teams.items()}
        
    data['team_name'] = data['teamId'].map(team_id_to_name)
    data['opponent_name'] = data['opponentid'].map(team_id_to_name)
    
    team = team.replace('-', '_')                                           
        
    data.to_csv(os.path.join(
        data_download_loc,
        f'{team}_data.csv'), index=False)
    
    create_table_whoscored(data, 
                 league = f'{league}', 
                 team = f'{team}')
        
        
    
    
    