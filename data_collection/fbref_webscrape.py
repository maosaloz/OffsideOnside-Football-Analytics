from functools import lru_cache
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import statistics
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore")
import requests
from bs4 import BeautifulSoup, Comment
import os
from pathlib import Path
import time
from scipy import stats
from statistics import mean
from math import pi
from utilities import comps_postgres_t5, comps_next7, comps_postgres_next7, comps_seasons_next7, ssns, create_table_fbref_goalkeeper, create_table_fbref_outfield

root = '/Users/Mao/Documents/GitHub/OffsideOnside-Football-Analytics/'
season = '2024-2025'
date_today = '25723'

def scrape_fbref_t5_leagues_players(season):
    # File names to change if needed
    raw_nongk = f'Raw FBRef {season}'
    raw_gk = f'Raw FBRef GK {season}'
    final_nongk = f'Final FBRef {season}'
    final_gk = f'Final FBRef GK {season}'

    # This section creates the programs that gather data from FBRef.com... Data is from FBRef and Opta
    def _get_table(soup):
        return soup.find_all('table')[0]

    def _get_opp_table(soup):
        return soup.find_all('table')[1]

    def _parse_row(row):
        cols = None
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        return cols

    def get_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        table = _get_table(soup)
        data = []
        headings=[]
        headtext = soup.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[1:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        return data

    def get_opp_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        table = _get_opp_table(soup)
        data = []
        headings=[]
        headtext = soup.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[1:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        return data


    # this section gets the raw tables from FBRef.com

    standard = "https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats"
    shooting = "https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats"
    passing = "https://fbref.com/en/comps/Big5/passing/players/Big-5-European-Leagues-Stats"
    pass_types = "https://fbref.com/en/comps/Big5/passing_types/players/Big-5-European-Leagues-Stats"
    gsca = "https://fbref.com/en/comps/Big5/gca/players/Big-5-European-Leagues-Stats"
    defense = "https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats"
    poss = "https://fbref.com/en/comps/Big5/possession/players/Big-5-European-Leagues-Stats"
    misc = "https://fbref.com/en/comps/Big5/misc/players/Big-5-European-Leagues-Stats"

    df_standard = get_df(standard)
    df_shooting = get_df(shooting)
    df_passing = get_df(passing)
    df_pass_types = get_df(pass_types)
    df_gsca = get_df(gsca)
    df_defense = get_df(defense)
    df_poss = get_df(poss)
    df_misc = get_df(misc)

    # this section sorts the raw tables then resets their indexes. Without this step, you will
    # run into issues with players who play minutes for 2 clubs in a season.

    df_standard.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_shooting.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_passing.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_pass_types.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_gsca.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_defense.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_poss.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_misc.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)

    df_standard = df_standard.reset_index(drop=True)
    df_shooting = df_shooting.reset_index(drop=True)
    df_passing = df_passing.reset_index(drop=True)
    df_pass_types = df_pass_types.reset_index(drop=True)
    df_gsca = df_gsca.reset_index(drop=True)
    df_defense = df_defense.reset_index(drop=True)
    df_poss = df_poss.reset_index(drop=True)
    df_misc = df_misc.reset_index(drop=True)

    df = df_standard.iloc[:, 0:10]
    df = df.join(df_standard.iloc[:, 13])
    #df = df.join(df_standard.iloc[:, 26])
    df.columns = df.columns.str.lower()
    df = df.rename(columns={'pos': 'position', 'squad':'club', 'born':'year', 'mp': 'matches', 'min': 'minutes', 'g+a':'g_a'})

    df = df.join(df_shooting.iloc[:,8:25])
    df = df.rename(columns={'Gls':'goals', 'Sh': 'shots', 'SoT': 'shots_t', 'SoT%': 'per_shots_t', 'Sh/90': 'shots_90', 'SoT/90': 'shots_t_90', 'G/Sh': 'g_shots', 'G/SoT': 'g_shots_t', 'Dist': 'avg_shot_dist', 'FK': 'fk_shots', 'PK':'pk', 'PKatt': 'pk_att', 'npxG/Sh': 'npxg_shots', 'G-xG': 'g_minus_xg', 'np:G-xG': 'npg_minus_npxg'})

    df = df.join(df_passing.iloc[:,8:13])
    df = df.rename(columns={'Cmp': 'pass_cmp', 'Att': 'pass_att', 'Cmp%': 'per_pass_cmp', 'TotDist': 'total_pass_dist', 'PrgDist': 'prog_pass_dist', })
    df = df.join(df_passing.iloc[:,13:16])
    df = df.rename(columns={'Cmp': 'short_pass_cmp', 'Att': 'short_pass_att', 'Cmp%': 'per_short_pass_cmp'})
    df = df.join(df_passing.iloc[:,16:19])
    df = df.rename(columns={'Cmp': 'med_pass_cmp', 'Att': 'med_pass_att', 'Cmp%': 'per_med_pass_cmp'})
    df = df.join(df_passing.iloc[:,19:22])
    df = df.rename(columns={'Cmp': 'long_pass_cmp', 'Att': 'long_pass_att', 'Cmp%': 'per_long_pass_cmp', })
    df = df.join(df_passing.iloc[:,22:31])
    df = df.rename(columns={'Ast': 'assists', 'xAG':'xag', 'xA': 'xa', 'A-xAG':'a_minus_xag', 'KP': 'key_passes', '1/3': 'final_third_cmp', 'PPA': 'pen_area_cmp', 'CrsPA': 'crs_pen_area_cmp', 'PrgP': 'prg_p', })

    df = df.join(df_pass_types.iloc[:, 9:23])
    df = df.rename(columns={'Live': 'live_pass', 'Dead': 'dead_pass', 'FK': 'fk_passes', 'TB': 'thru_balls', 'Sw': 'switches', 'Crs': 'crosses', 'CK': 'ck', 'In': 'inswing_ck', 'Out': 'outswing_ck', 'Str': 'straight_ck', 'TI': 'throw_ins', 'Off': 'passes_to_off', 'Blocks':'passes_blocked', 'Cmp':'cmpxxx'})

    df = df.join(df_gsca.iloc[:, 8:16].rename(columns={'SCA': 'sc_actions', 'SCA90': 'sc_actions_90', 'PassLive': 'sca_live_pass', 'PassDead': 'sca_dead_pass', 'TO': 'sca_take_on', 'Sh': 'sca_shot', 'Fld': 'sca_fouls', 'Def': 'sca_def_actions'}))
    df = df.join(df_gsca.iloc[:, 16:24].rename(columns={'GCA': 'gc_actions', 'GCA90': 'gc_actions_90', 'PassLive': 'gca_live_pass', 'PassDead': 'gca_dead_pass', 'TO': 'gca_take_on', 'Sh': 'gca_shot', 'Fld': 'gca_fouls', 'Def': 'gca_def_actions'}))

    df = df.join(df_defense.iloc[:,8:13].rename(columns={'Tkl': 'tackles', 'TklW': 'tackles_won', 'Def 3rd': 'tackles_def_third', 'Mid 3rd': 'tackles_mid_third', 'Att 3rd': 'tackles_att_third'}))
    df = df.join(df_defense.iloc[:,13:24].rename(columns={'Tkl': 'drib_tackles', 'Att': 'drib_attempted', 'Tkl%': 'per_drib_tackled', 'Lost': 'drib_lost', 'Blocks': 'blocks', 'Sh': 'shot_blocks', 'Pass': 'pass_blocks', 'Int': 'interceptions', 'Tkl+Int': 'tackles_interceptions', 'Clr': 'clearances', 'Err': 'shot_errors'}))

    df = df.join(df_poss.iloc[:,8:30])
    df = df.rename(columns={'Touches': 'touches', 'Def Pen': 'touches_def_pen', 'Def 3rd': 'touches_def_third', 'Mid 3rd': 'touches_mid_third', 'Att 3rd': 'touches_att_third', 'Att Pen': 'touches_att_pen', 'Live': 'live_touches', 'Succ': 'take_ons_success', 'Att': 'take_ons_attempted', 'Succ%': 'per_take_ons_success', 
                            'Tkld':'take_ons_tackled', 'Tkld%':'per_take_ons_tackled', 'Carries':'carries', 'TotDist':'dist_carries', 'PrgDist':'prog_dist_carries', 'PrgC':'prog_carries', '1/3':'carries_att_third', 'CPA':'carries_att_pen', 'Mis': 'miscontrols', 'Dis': 'dispossessions', 'Rec': 'pass_rec', 'PrgR':'prog_pass_rec'})

    df = df.join(df_misc.iloc[:, 8:14])
    # yellows: number of yellow cards collected 
    # reds: number of red cards collected 
    # second_yellow: number of second yellow cards collected in a match
    # fouls_committed: number of fouls committed by player
    # fouls_drawn: number of fouls drawn by player
    # offsides: number of time caught offsides
    df = df.rename(columns={'CrdY': 'yellows', 'CrdR': 'reds', '2CrdY': 'second_yellow', 'Fls': 'fouls_committed', 'Fld': 'fouls_drawn', 'Off': 'Off', })
    df = df.join(df_misc.iloc[:,17:24])
    # pk_wins: number of penalty kicks won by player 
    # pk_drawn: number of penalty kicks conceeded by player
    # balls_recovered: number of balls recovered
    # aerial_wins: number of aerial duels won by player
    # aerial_losses: number of aerial duals lost by player
    # per_aerial_wins: percentage of aerial duels won
    df = df.rename(columns={'PKwon': 'pk_wins', 'PKcon': 'pk_drawn', 'Recov': 'balls_recovered', 'Won': 'aerial_wins', 'Lost': 'aerial_losses', 'Won%': 'per_aerial_wins' })

    # Make sure to drop all blank rows (FBRef's tables have several)
    df.dropna(subset = ["player"], inplace=True)

    # Turn the minutes columns to integers. So from '1,500' to '1500'. Otherwise it can't do calculations with minutes
    for i in range(0,len(df)):
        df.iloc[i][9] = df.iloc[i][9].replace(',','')
    df.iloc[:,9:] = df.iloc[:,9:].apply(pd.to_numeric)

    # Store the file
    df_raw_nongk = df.copy()


    ##################################################################################
    ############################## GK SECTION ########################################
    ##################################################################################

    gk = "https://fbref.com/en/comps/Big5/keepers/players/Big-5-European-Leagues-Stats"
    advgk = "https://fbref.com/en/comps/Big5/keepersadv/players/Big-5-European-Leagues-Stats"

    df_gk = get_df(gk)
    df_advgk = get_df(advgk)

    df_gk.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_advgk.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)

    df_gk = df_gk.reset_index(drop=True)
    df_advgk = df_advgk.reset_index(drop=True)

    ###############################################################################
    
    
    df = df[df['position'].str.contains("GK")].reset_index().iloc[:,1:]
    df_gk['Pos'] = df_gk['Pos'].astype(str)
    df_gk = df_gk[df_gk['Pos'].str.contains('GK')]
    df_gk = df_gk.reset_index().iloc[:,1:]
    df_gk.columns.values[15] = 'Save%.1'
    df_gk.columns.values[25] = 'Save%.2'
    df = df.join(df_gk.iloc[:, 11:26].astype(float), lsuffix='.1', rsuffix='.2')
    # GA: Goals against
    # GA90: Goals against per 90 minutes 
    # shots_ota: Shots on target against
    # Saves: saves 
    # per_saves: save percentage (i.e. (shots on target against - goals against)/shots on target against)
    # clean_sheets: clean sheets
    # per_clean_sheets: percentage of matches that end in clean sheets
    # pk_faced: number of penalty kicks faced 
    # pk_allowed: number of penalty kicks scored against goalkeeper
    # pk_saved: number of penalty kicks saved by goalkeeper
    # pk_missed: number of penalty kicks missed by opposing player
    # per_pk_saves: percentage of penalty kicks saved
    df = df.rename(columns={'Player':'player', 'Nation':'nation', 'Squad': 'club', 'Comp': 'comp', 'Age': 'age', 'Born':'year', 'MP': 'matches', 'Starts': 'starts', 'Min': 'minutes',
                                  'SoTA':'shots_ota', 'Saves':'saves', 'Save%.1':'per_saves', 'W':'wins', 'D':'draws', 'L':'losses', 'CS':'clean_sheets', 'CS%':'per_clean_sheets', 'PKatt':'pk_faced',
                                  'PKA': 'pk_allowed', 'PKsv': 'pk_saved', 'PKm':'pk_missed', 'Save%.2':'per_pk_saves'})

    df_advgk['Pos'] = df_advgk['Pos'].astype(str)
    df_advgk = df_advgk[df_advgk['Pos'].str.contains('GK')]
    df_advgk = df_advgk.reset_index().iloc[:,1:]
    # pk_gc: penalty kick goals conceeded 
    # fk_gc: freekick goals conceeded
    # ck_gc: corner kick goals conceeded
    # og_c: own goals conceeded on goalkeeper
    # post_shot_xg: expected goals based on how likely the goalkeeper is to save the shot
    # post_shot_xg_per_shot_t: Post shot expected goals per shot on target (a higher index means shots on target are more difficult to stop and more likely to score)
    # post_shot_xg_plus_minus: post shot expected goals minus goals allowed (postive numbers indicates an above average ability to stop shot)
    # post_shot_xg_plus_minus_90: post shot expected goals minus goals allowed per 90 minutes (postive numbers indicates an above average ability to stop shot)
    # launched_pass_cmp: passes launched further than 40 yards that are completed  
    # launched_pass_att: passes launched further than 40 yards that are attempted
    # per_launch_pass_cmp: percentage of launched passes that are completed 
    df = df.join(df_advgk.iloc[:,9:20].astype(float).rename(columns={'PKA': 'pk_gc', 'FK': 'fk_gc', 'CK': 'ck_gc', 'OG': 'OG_c', 'PSxG': 'post_shot_xg', 'PSxG/SoT': 'post_shot_xg_per_shot_t', 'PSxG+/-': 'post_shot_xg_plus_minus', '/90': 'post_shot_xg_plus_minus_90', 'Cmp': 'launched_pass_cmp', 'Att': 'launched_pass_att', 'Cmp%': 'per_launch_pass_cmp'}))
    # pass_att: passes attempted not including goalkicks
    # pass_throw: thrown passes attempted
    # per_pass_launched: percentage of passes that were launched
    # avg_launch_len: average length of passes 
    df = df.join(df_advgk.iloc[:,20:24].astype(float).rename(columns={'Att (GK)': 'pass_att_gk', 'Thr': 'pass_thow', 'Launch%': 'per_pass_launched', 'AvgLen': 'avg_len'}))
    # gk_att: goalkicks attempted
    # per_gk_launched: percentage of goalkicks that were launched 
    # gk_avg_len: average length of goalkicks in yards
    # opp_crosses: number of crosses faced by goalkeeper 
    # stop_crosses: crosses stopped by goalkeeper
    # per_stop_crosses: percentage of crosses stopped 
    # def_actions_opa: defensive actions outside of penalty area 
    # def_actions_opa_90: defensive actions outside of penalty area per 90 minutes 
    # avg_dist_def_actions: average distance away from goal (in yards) of all defensive actions
    df = df.join(df_advgk.iloc[:,24:33].astype(float).rename(columns={'Att': 'gk_att', 'Launch%': 'per_gk_launched', 'AvgLen': 'gk_avg_len', 'Opp': 'opp_crosses', 'Stp': 'stop_crosses', 'Stp%': 'per_stop_crosses', '#OPA': 'def_actions_opa', '#OPA/90': 'def_actions_opa_90', 'AvgDist': 'avg_dist_def_actions'}))

    df_raw_gk = df.copy()

    ##################################################################################
    ##################### Final file for outfield data ###############################
    ##################################################################################

    df = df_raw_nongk.copy()
    df_90s = df_raw_nongk.copy()
    df_90s['minutes'] = pd.to_numeric(df_90s['minutes'], errors='coerce').astype('float')
    df_90s['90s'] = df_90s['minutes']/90
    cols = df_90s.columns.tolist()
    minutes_idx = cols.index('minutes')
    cols.remove('90s')
    cols.insert(minutes_idx + 1, '90s')
    df_90s = df_90s[cols]
    for i in range(11,125):
        df_90s.iloc[:,i] = df_90s.iloc[:,i]/df_90s['90s']
    
    df_90s = df_90s.iloc[:,11:].add_suffix('Per90')
    df_new = df.join(df_90s)

    try:
        for i in range(len(df_new)):
            df_new['age'][i] = int(df_new['age'][i][:2])
    except:
        pass

    df_final_nongk = df_new.copy()


    ##################################################################################
    ##################### Final file for keeper data #################################
    ##################################################################################

    df = df_raw_gk.copy()
    df_90s = df_raw_gk.copy()
    df_90s['minutes'] = pd.to_numeric(df_90s['minutes'], errors='coerce').astype('float')
    df_90s['90s'] = df_90s['minutes']/90
    cols = df_90s.columns.tolist()
    minutes_idx = cols.index('minutes')
    cols.remove('90s')
    cols.insert(minutes_idx + 1, '90s')
    df_90s = df_90s[cols]
    for i in range(11,164):
        df_90s.iloc[:,i] = df_90s.iloc[:,i]/df_90s['90s']
    df_90s = df_90s.iloc[:,11:].add_suffix('Per90')
    df_new = df.join(df_90s)

    try:
        for i in range(len(df_new)):
            df_new['age'][i] = int(df_new['age'][i][:2])
    except:
        pass

    df_final_gk = df_new.copy()
    

    ##################################################################################
    ################ Download team data, for possession-adjusting ####################
    ##################################################################################

    standard = "https://fbref.com/en/comps/Big5/stats/squads/Big-5-European-Leagues-Stats"
    poss = "https://fbref.com/en/comps/Big5/possession/squads/Big-5-European-Leagues-Stats"

    df_standard = get_df(standard)
    df_poss = get_df(poss)

    df_standard = df_standard.reset_index(drop=True)
    df_poss = df_poss.reset_index(drop=True)

    ############################################

    df = df_standard.iloc[:, 0:30]

    # Gets the number of touches a team has per 90
    df['TeamTouches90'] = float(0.0)
    for i in range(len(df)):
        df.iloc[i,30] = float(df_poss.iloc[i,5]) / float(df_poss.iloc[i,4])

    # Take out the comma in minutes like above
    for j in range(0,len(df)):
        df.at[j,'Min'] = df.at[j,'Min'].replace(',','')
    df.iloc[:,7:] = df.iloc[:,7:].apply(pd.to_numeric)

    df_final_nongk_teams = df.copy()


    ##################################################################################
    ################ Download opposition data, for possession-adjusting ##############
    ##################################################################################

    opp_poss = "https://fbref.com/en/comps/Big5/possession/squads/Big-5-European-Leagues-Stats"

    df_opp_poss = get_opp_df(opp_poss)
    df_opp_poss = df_opp_poss.reset_index(drop=True)

    ############################################

    df = df_opp_poss.iloc[:, 0:15]
    df = df.rename(columns={'Touches':'Opp Touches'})
    df = df.reset_index()

    #############################################

    df1 = df_final_nongk_teams.copy()

    df1['Opp Touches'] = 1
    for i in range(len(df1)):
        df1['Opp Touches'][i] = df['Opp Touches'][i]
    df1 = df1.rename(columns={'Min':'Team Min'})

    df_final_nongk_teams = df1.copy()

    ##################################################################################
    ################ Make the final, complete, outfield data file ####################
    ##################################################################################

    df = df_final_nongk.copy()
    teams = df_final_nongk_teams.copy()

    df['AvgTeamPoss'] = float(0.0)
    df['OppTouches'] = int(1)
    df['TeamMins'] = int(1)
    df['TeamTouches90'] = float(0.0)

    player_list = list(df['player'])

    for i in range(len(player_list)):
        team_name = df[df['player']==player_list[i]]['club'].values[0]
        team_poss = teams[teams['Squad']==team_name]['Poss'].values[0]
        opp_touch = teams[teams['Squad']==team_name]['Opp Touches'].values[0]
        team_mins = teams[teams['Squad']==team_name]['Team Min'].values[0]
        team_touches = teams[teams['Squad']==team_name]['TeamTouches90'].values[0]
        df.at[i, 'AvgTeamPoss'] = team_poss
        df.at[i, 'OppTouches'] = opp_touch
        df.at[i, 'TeamMins'] = team_mins
        df.at[i, 'TeamTouches90'] = team_touches

    df.iloc[:,9:] = df.iloc[:,9:].astype(float)
    # All of these are the possession-adjusted columns. A couple touch-adjusted ones at the bottom
    df['pAdj_tackles_interceptionsPer90'] = (df['tackles_interceptionsPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_clearancesPer90'] = (df['clearancesPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_shot_blocksPer90'] = (df['shot_blocksPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_pass_blocksPer90'] = (df['pass_blocksPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_interceptionsPer90'] = (df['interceptionsPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_drib_tacklesPer90'] = (df['drib_tacklesPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_drib_lostPer90'] = (df['drib_lostPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_aerial_winsPer90'] = (df['aerial_winsPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_aerial_lossesPer90'] = (df['aerial_lossesPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_drib_attemptedPer90'] = (df['drib_attemptedPer90']/(100-df['AvgTeamPoss']))*50
    df['touch_centrality'] = (df['touchesPer90']/df['TeamTouches90'])*100
    df['tackles_interceptionsPer600OppTouch'] = df['tackles_interceptions'] /(df['OppTouches']*(df['minutes']/df['TeamMins']))*600
    df['pAdj_touchesPer90'] = (df['touchesPer90']/(df['AvgTeamPoss']))*50
    df['carriesPer50Touches'] = df['carries'] / df['touches'] * 50
    df['prog_carriesPer50Touches'] = df['prog_carries'] / df['touches'] * 50
    df['prog_passesPer50CmpPasses'] = df['prg_p'] / df['pass_cmp'] * 50

    # Now we'll add the players' actual positions, from @jaseziv, into the file
    tm_pos = pd.read_csv('https://github.com/griffisben/Soccer-Analyses/blob/main/TransfermarktPositions-Jase_Ziv83.csv?raw=true')
    tm_pos.rename(columns={'Player': 'player'}, inplace=True)
    df = pd.merge(df, tm_pos, on ='player', how ='left')

    for i in range(len(df)):
        if df.position[i] == 'GK':
            df['Main Position'][i] = 'Goalkeeper'
    df.to_csv(os.path.join(root, f'Final FBRef {season}.csv'))


    ##################################################################################
    ################ Make the final, complete, keepers data file #####################
    ##################################################################################

    df = df_final_gk.copy()
    teams = df_final_nongk_teams.copy()

    df['AvgTeamPoss'] = float(0.0)
    df['OppTouches'] = float(0.0)
    df['TeamMins'] = float(0.0)
    df['TeamTouches90'] = float(0.0)

    player_list = list(df['player'])

    for i in range(len(player_list)):
        team_name = df[df['player']==player_list[i]]['club'].values[0]
        team_poss = teams[teams['Squad']==team_name]['Poss'].values[0]
        opp_touch = teams[teams['Squad']==team_name]['Opp Touches'].values[0]
        team_mins = teams[teams['Squad']==team_name]['Team Min'].values[0]
        team_touches = teams[teams['Squad']==team_name]['TeamTouches90'].values[0]
        df.at[i, 'AvgTeamPoss'] = team_poss
        df.at[i, 'OppTouches'] = opp_touch
        df.at[i, 'TeamMins'] = team_mins
        df.at[i, 'TeamTouches90'] = team_touches

    df.iloc[:,9:] = df.iloc[:,9:].astype(float)
    # Same thing, makes pAdj stats for the GK file
    df['pAdj_tackles_interceptionsPer90'] = (df['tackles_interceptionsPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_clearancesPer90'] = (df['clearancesPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_shot_blocksPer90'] = (df['shot_blocksPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_pass_blocksPer90'] = (df['pass_blocksPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_interceptionsPer90'] = (df['interceptionsPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_drib_tacklesPer90'] = (df['drib_tacklesPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_drib_lostPer90'] = (df['drib_lostPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_aerial_winsPer90'] = (df['aerial_winsPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_aerial_lossesPer90'] = (df['aerial_lossesPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdj_drib_attemptedPer90'] = (df['drib_attemptedPer90']/(100-df['AvgTeamPoss']))*50
    df['touch_centrality'] = (df['touchesPer90']/df['TeamTouches90'])*100
    df['tackles_interceptionsPer600OppTouch'] = df['tackles_interceptions'] /(df['OppTouches']*(df['minutes']/df['TeamMins']))*600
    df['pAdj_touchesPer90'] = (df['touchesPer90']/(df['AvgTeamPoss']))*50
    df['carriesPer50Touches'] = df['carries'] / df['touches'] * 50
    df['prog_carriesPer50Touches'] = df['prog_carries'] / df['touches'] * 50
    df['prog_passesPer50CmpPasses'] = df['prg_p'] / df['pass_cmp'] * 50


    # Just adding the main positions to the GK too, but of course, they will all be GK lol. Keeps other program variables clean
    tm_pos = pd.read_csv('https://github.com/griffisben/Soccer-Analyses/blob/main/TransfermarktPositions-Jase_Ziv83.csv?raw=true')
    tm_pos.rename(columns={'Player': 'player'}, inplace=True)
    df = pd.merge(df, tm_pos, on ='player', how ='left')

    for i in range(len(df)):
        if df.position[i] == 'GK':
            df['Main Position'][i] = 'Goalkeeper'
    df.to_csv(os.path.join(root, f'Final FBRef GK {season}.csv'))
    print(f'Done :) Files are located at  %s/Final FBRef {season}.csv' %root)

scrape_fbref_t5_leagues_players(season=season)

for comp, postgres in comps_postgres_t5.items():
    
    data = pd.read_csv(os.path.join(
        root,
        f"Final FBRef {season}.csv"))
    
    data['comp'] = data['comp'].str.split(' ', 1).str[1]
    data = data[data['comp']==comp]
    
    data = data.loc[:, ~data.columns.duplicated()]
    
    create_table_fbref_outfield(data=data, comp=comp, season=season, postgres=postgres, date=date_today)
    
    data = pd.read_csv(os.path.join(
        root,
        f"Final FBRef GK {season}.csv"))
    
    data['comp'] = data['comp'].str.split(' ', 1).str[1]
    
    data = data.loc[:, ~data.columns.duplicated()]
    data = data[data['comp']==comp]
    
    data.drop(columns=['position', 'goals', 'assists', 'g_a', 'pk', 'pk_att',  'prg_p', 'shots_90', 
                       'shots', 'shots_t', 'per_shots_t', 'shots_t_90', 'g_shots', 'g_shots_t', 'fk_shots',
                       'xG', 'npxG', 'npxg_shots', 'g_minus_xg', 'npg_minus_npxg', 'xag', 'a_minus_xag', 'thru_balls',
                       'throw_ins', 'ck', 'inswing_ck', 'outswing_ck', 'straight_ck', 'sca_take_on', 'sca_shot', 'sca_fouls',
                       'sca_def_actions', 'gc_actions', 'gc_actions_90', 'gca_live_pass', 'gca_dead_pass', 'gca_take_on',
                       'gca_shot', 'gca_fouls', 'gca_def_actions', 'tackles_won', 'tackles_def_third', 'tackles_mid_third',
                       'tackles_att_third', 'drib_tackles', 'drib_attempted', 'per_drib_tackled', 'drib_lost', 'blocks',
                       'shot_blocks', 'pass_blocks', 'interceptions', 'tackles_interceptions', 'shot_errors',
                       'touches_att_third', 'touches_att_pen', 'take_ons_attempted', 'take_ons_success', 'per_take_ons_success',
                       'take_ons_tackled', 'per_take_ons_tackled', 'prog_carries', 'carries_att_third', 'carries_att_pen',
                       'prog_pass_rec', 'avg_shot_dist',
                       'goalsPer90', 'assistsPer90', 'g_aPer90',  'pkPer90', 'pk_attPer90', 'prg_pPer90', 'shots_90Per90',
                       'shotsPer90', 'shots_tPer90', 'per_shots_tPer90', 'shots_t_90Per90', 'g_shotsPer90', 'g_shots_tPer90', 'fk_shotsPer90',
                       'xGPer90', 'npxGPer90', 'npxg_shotsPer90', 'g_minus_xgPer90', 'npg_minus_npxgPer90', 'xagPer90', 'a_minus_xagPer90', 'thru_ballsPer90',
                       'throw_insPer90', 'ckPer90', 'inswing_ckPer90', 'outswing_ckPer90', 'straight_ckPer90', 'sca_take_onPer90', 'sca_shotPer90', 'sca_foulsPer90',
                       'sca_def_actionsPer90', 'gc_actionsPer90', 'gc_actions_90Per90', 'gca_live_passPer90', 'gca_dead_passPer90', 'gca_take_onPer90',
                       'gca_shotPer90', 'gca_foulsPer90', 'gca_def_actionsPer90', 'tackles_wonPer90', 'tackles_def_thirdPer90', 'tackles_mid_thirdPer90',
                       'tackles_att_thirdPer90', 'drib_tacklesPer90', 'drib_attemptedPer90', 'per_drib_tackledPer90', 'drib_lostPer90', 'blocksPer90',
                       'shot_blocksPer90', 'pass_blocksPer90', 'interceptionsPer90', 'tackles_interceptionsPer90', 'shot_errorsPer90',
                       'touches_att_thirdPer90', 'touches_att_penPer90', 'take_ons_attemptedPer90', 'take_ons_successPer90', 'per_take_ons_successPer90',
                       'take_ons_tackledPer90', 'per_take_ons_tackledPer90', 'prog_carriesPer90', 'carries_att_thirdPer90', 'carries_att_penPer90',
                       'prog_pass_recPer90', 'avg_shot_distPer90'], inplace=True)
    
    create_table_fbref_goalkeeper(data=data, season=season, postgres=postgres, date=date_today)
   


def scrape_fbref_next12_leagues_players(comps, seasons):
    def _get_table(soup):
        return soup.find_all('table')[0]

    def _get_opp_table(soup):
        return soup.find_all('table')[1]

    def _parse_row(row):
        cols = None
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        return cols

    def _parse_team_row(row):
        cols = None
        cols = row.find_all(['td', 'th'])
        cols = [ele.text.strip() for ele in cols]
        return cols

    def get_players_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        comment = soup.find_all(text=lambda t: isinstance(t, Comment))
        c=0
        for i in range(len(comment)):
            if comment[i].find('\n\n<div class="table_container"') != -1:
                c = i
        a = comment[c]
        tbody = a.find('table')
        sp = BeautifulSoup(a[tbody:], 'html.parser')
        table = _get_table(sp)
        data = []
        headings=[]
        headtext = sp.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[1:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        data.insert(4, 'Comp', [comp]*len(data))
        return data

    def get_team_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        table = _get_table(soup)
        data = []
        headings=[]
        headtext = soup.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[0:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_team_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        data.insert(1, 'Comp', [comp]*len(data))
        return data


    def get_opp_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        table = _get_opp_table(soup)
        data = []
        headings=[]
        headtext = soup.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[0:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_team_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        data.insert(1, 'Comp', [comp]*len(data))
        return data

    for k in range(len(comps_next7)):
        season = seasons[k]
        comp = comps[k]
        print('Working on %s' %comp)

        raw_nongk = 'Raw FBRef %s - %s' %(season,comp)
        raw_gk = 'Raw FBRef GK %s - %s' %(season,comp)
        final_nongk = 'Final FBRef %s - %s' %(season,comp)
        final_gk = 'Final FBRef GK %s - %s' %(season,comp)

        if comp == 'MLS':
            lg_str = 'Major-League-Soccer'
            lg_id = 22
        if comp == 'Brasileirão':
            lg_str = 'Serie-A'
            lg_id = 24
        if comp == 'Eredivisie':
            lg_str = 'Eredivisie'
            lg_id = 23
        if comp == 'Primeira Liga':
            lg_str = 'Primeira-Liga'
            lg_id = 32
        if comp == 'Championship':
            lg_str = 'Championship'
            lg_id = 10
        if comp == 'Belgian Pro League':
            lg_str = 'Belgian-Pro-League'
            lg_id = 37
        if comp == 'Argentine Primera División':
            lg_str = 'Primera-Division'
            lg_id = 21


        # this section gets the raw tables from FBRef.com
        standard = "https://fbref.com/en/comps/%i/stats/%s-Stats" %(lg_id, lg_str)
        shooting = "https://fbref.com/en/comps/%i/shooting/%s-Stats" %(lg_id, lg_str)
        passing = "https://fbref.com/en/comps/%i/passing/players/%s-Stats" %(lg_id, lg_str)
        pass_types = "https://fbref.com/en/comps/%i/passing_types/players/%s-Stats" %(lg_id, lg_str)
        gsca = "https://fbref.com/en/comps/%i/gca/players/%s-Stats" %(lg_id, lg_str)
        defense = "https://fbref.com/en/comps/%i/defense/players/%s-Stats" %(lg_id, lg_str)
        poss = "https://fbref.com/en/comps/%i/possession/players/%s-Stats" %(lg_id, lg_str)
        #misc = "https://fbref.com/en/comps/%i/misc/players/%s-Stats" %(lg_id, lg_str)

        df_standard = get_players_df(standard)
        df_shooting = get_players_df(shooting)
        df_passing = get_players_df(passing)
        df_pass_types = get_players_df(pass_types)
        df_gsca = get_players_df(gsca)
        df_defense = get_players_df(defense)
        df_poss = get_players_df(poss)
        #df_misc = get_players_df(misc)

        # this section sorts the raw tables then resets their indexes. Without this step, you will
        # run into issues with players who play minutes for 2 clubs in a season.

        df_standard.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_shooting.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_passing.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_pass_types.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_gsca.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_defense.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_poss.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        #df_misc.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)

        df_standard = df_standard.reset_index(drop=True)
        df_shooting = df_shooting.reset_index(drop=True)
        df_passing = df_passing.reset_index(drop=True)
        df_pass_types = df_pass_types.reset_index(drop=True)
        df_gsca = df_gsca.reset_index(drop=True)
        df_defense = df_defense.reset_index(drop=True)
        df_poss = df_poss.reset_index(drop=True)
        #df_misc = df_misc.reset_index(drop=True)

        # Merging all the dataframes to df 
        
        # df_standard
        df = df_standard.iloc[:, 0:17]
        try:
            df_standard = df_standard.iloc[:, :26]                                      # Removing stats per 90
            df = df.join(df_standard[['PrgC', 'PrgP', 'PrgR']])
        except Exception as e:
            print(f"Stanadard data: PrgC, PrgP, PrgR missing") 
        # player: Player
        # nation: nationality of the player 
        # position: Habitual position of the player
        # club: Club team that the player plays for 
        # comp: competition which the players club plays in
        # age: Age in years and days of each player 
        # year: The year in which the player was born in  
        # matches: Number of matches in which the player has played in 
        # starts: Number of matches for which the player was included in the starting lineup 
        # minutes: Total minutes the player has played throughout the season 
        # 90s: number of minutes a player has played in divided by 90 minutes (full matches)
        # goals: Goals
        # assists: Assists
        # g_a: Total goals + assists
        # np_goals: Total non-penalty goals
        # pk: Penalty kicks made
        # pk_att: Penalty kicks attempted
        # g_a_minus_pk_90: Non penalty goals + assists per 90 minutes
        # prg_c: Progressive carries (moving the ball closer to the opponents goal line by at least 10-yards, excludes carries which end in the defending 50% of the pitch)
        # prg_p: Progressive passes (moving the ball closer to the opponents goal line by at least 10-yards, excludes passes passes from the defending 40% of the pitch)
        # prg_r: Progressive passes received (moving the ball closer to the opponents goal line by at least 10-yards, excludes passes passes from the defending 40% of the pitch)
        df.rename(columns={'Player': 'player', 'Nation': 'nation', 'Pos': 'position', 'Squad': 'club', 'Comp': 'comp', 'Age': 'age', 'Born': 'year', 'MP': 'matches', 'Starts': 'starts', 'Min': 'minutes', 'G+A': 'g_a', 'PK': 'pk', 'PKatt': 'pk_att', 'G+A-PK': 'g_a_minus_pk_90', 'G-PK': 'np_goals', 'Gls':'goals', 'Ast': 'assists', 'PrgC': 'prg_c', 'PrgP': 'prg_p', 'PrgR': 'prg_r'}, inplace=True)
        
        # df_shooting
        df = df.join(df_shooting.iloc[:,9:16])
        try:
            df = df.join(df_shooting[['FK', 'xG', 'npxG', 'npxG/Sh', 'G-xG', 'np:G-xG']])
        except Exception as e:
            print(f"Shooting data: FKShots, xG, npxG, npxG/Shots, G-xG, npG-npxG missing")
        # shots: Total number of shots
        # shots_t: Total number of shots on target
        # per_shots_t: Percentage of shots that are on target
        # shots_90: Total shots per 90 minutes 
        # shots_t_90: Shots on target per 90 minutes 
        # g_shots: Goals per shot
        # g_shots_t: Goals per shots on target
        # avg_shot_dist: Average shot distance
        # fk_shots: Shots from freekicks 
        # xg: Expected goals 
        # npxg: Non-penalty expected goals 
        # npxg_shots: Non-penalty expected goals per shot 
        # g_minus_xg: Goals minus expected goals 
        # npg_minus_npxg: Non-penalty goals minus non-penalty expected goals 
        df.rename(columns={'Sh': 'shots', 'SoT': 'shots_t', 'SoT%': 'per_shots_t', 'Sh/90': 'shots_90', 'SoT/90': 'shots_t_90', 'G/Sh': 'g_shots', 'G/SoT': 'g_shots_t', 'Dist': 'avg_shot_dist', 'FK': 'fk_shots', 'npxG/Sh': 'npxg_shots', 'G-xG': 'g_minus_xg', 'np:G-xG': 'npg_minus_npxg'}, inplace=True)
        
        # df_passing
        df = df.join(df_passing.iloc[:,8:13])
        # pass_cmp: Passes completed 
        # pass_att: Passes attempted 
        # per_pass_cmp: Passes completion rate
        # total_pass_dist: Total passing distance 
        # prog_pass_dist: Progressive passing distance 
        df = df.rename(columns={'Cmp': 'pass_cmp', 'Att': 'pass_att', 'Cmp%': 'per_pass_cmp', 'TotDist': 'total_pass_dist', 'PrgDist': 'prog_pass_dist'})
        
        df = df.join(df_passing.iloc[:,13:16])
        # short_pass_cmp: Short passes completed (passes between 5 and 15 yards)
        # short_pass_att: Short passes attempted (passes between 5 and 15 yards)
        # per_short_pass_cmp: Short passes completion rate (passes between 5 and 15 yards)
        df = df.rename(columns={'Cmp': 'short_pass_cmp', 'Att': 'short_pass_att', 'Cmp%': 'per_short_pass_cmp'})
        
        df = df.join(df_passing.iloc[:,16:19])
        # med_pass_cmp: Medium passes completed (passes between 15 and 30 yards)
        # med_pass_att: Medium passes attempted (passes between 15 and 30 yards)
        # per_med_pass_cmp: Medium passes completion rate (passes between 15 and 30 yards)
        df = df.rename(columns={'Cmp': 'med_pass_cmp', 'Att': 'med_pass_att', 'Cmp%': 'per_med_pass_cmp'})
        
        df = df.join(df_passing.iloc[:,19:22])
        # long_pass_cmp: Long passes completed (passes longer than 30 yards)
        # long_pass_att: Long passes attempted (passes longer than 30 yards)
        # per_long_pass_cmp: Long passes completion rate (passes longer than 30 yards)
        df = df.rename(columns={'Cmp': 'long_pass_cmp', 'Att': 'long_pass_att', 'Cmp%': 'per_long_pass_cmp' })
        
        df = df.join(df_passing.iloc[:,23:28])
        # xag: Expected assisted goals (xG which follows a pass that assists a shot)
        # xa: Expected assists (likelihood each pass becomes a goal assist)
        # a-xag: Assists minus expected goals assisted 
        # key_passes: Passes that directly lead to a shot 
        # final_third_cmp: Completed passes that enter the final 1/3 of pitch closest to the goal not including set pieces 
        # pen_area_cmp: Passes into the penalty area not including set pieces 
        # crs_pen_area_cmp: Completed passes into the penalty box not including set pieces
        df = df.rename(columns={'xA': 'xa', 'xAG': 'xag', 'A-xAG': 'a_minus_xag', 'KP': 'key_passes', '1/3': 'final_third_cmp', 'PPA': 'pen_area_cmp', 'CrsPA': 'crs_pen_area_cmp'})

        df = df.join(df_pass_types.iloc[:, 9:23])
        # live_pass: Live-ball passes
        # dead_pass: Dead-ball passes includes free kicks, corner kicks kick offs, throw ins and goal kicks
        # fk_passes: Passes attempted from free kicks 
        # thru_balls: Completed passes sent between defenders into open space 
        # switches: Passes that travel more than 40 yards the width of the pitch 
        # crosses: Crosses
        # throw_ins: Throw-ins 
        # ck: corner kicks 
        # inswing_ck: Inswing corner kicks 
        # outswing_ck: Outswing corner kicks 
        # straight_ck: Straight corner kicks
        # passes_to_off: Passes offside
        # passes_blocked: Passes blocked by opponent
        # cmpxxx: passes completed from live_pass (including crosses), corner kicks (ck), throw-ins (throw_ins), free kicks (fk_passes) and goal kicks
        df = df.rename(columns={'Live': 'live_pass', 'Dead': 'dead_pass', 'FK': 'fk_passes', 'TB': 'thru_balls', 'Sw': 'switches', 'Crs': 'crosses', 'TI': 'throw_ins', 'CK': 'ck', 'In': 'inswing_ck', 'Out': 'outswing_ck', 'Str': 'straight_ck', 'Off': 'passes_to_off', 'Blocks':'passes_blocked', 'Cmp':'cmpxxx'})

        df = df.join(df_gsca.iloc[:, 9:16])
        # sc_actions: Shot-creating actions (the two offensive actions directly leading to a shot such as passes, take-ons, or drawing fouls) 
        # sc_actions_90: Shot-creating actions per 90 minutes 
        # sca_live_pass: Completed live-ball passes that lead to a shot attempt
        # sca_dead_pass: Completed dead-ball pass that lead to a shot attempt
        # sca_take_on: Successful take-ons that lead to a shot attempt
        # sca_shot: Shots that lead to another shot attempt
        # sca_fouls: Fouls drawn that lead to a shot attempt
        # sca_def_actions: Defensive actions that lead to a shot attempt 
        df.rename(columns={'SCA': 'sc_actions', 'SCA90': 'sc_actions_90', 'PassLive': 'sca_live_pass', 'PassDead': 'sca_dead_pass', 'TO': 'sca_take_on', 'Sh': 'sca_shot', 'Fld': 'sca_fouls', 'Def': 'sca_def_actions'}, inplace=True)
        
        df = df.join(df_gsca.iloc[:, 16:24])
        # gc_actions: Goal-creating actions (the two offensive actions directly leading to a shot such as passes, take-ons, or drawing fouls)
        # gc_actions_90: Goal-creating actions per 90 minutes 
        # gca_live_pass: Completed live-ball passes that lead to a goal
        # gca_dead_pass: Completed dead-ball pass that lead to a goal
        # gca_take_on: Successful take-ons that lead to a goal
        # gca_shot: Shots that lead to another goal-scoring shot
        # gca_fouls: Fouls drawn that lead to a goal
        # gca_def_actions: Defensive actions that lead to a goal 
        df.rename(columns={'GCA': 'gc_actions', 'GCA90': 'gc_actions_90', 'PassLive': 'gca_live_pass', 'PassDead': 'gca_dead_pass', 'TO': 'gca_take_on', 'Sh': 'gca_shot', 'Fld': 'gca_fouls', 'Def': 'gca_def_actions'}, inplace=True)

        df = df.join(df_defense.iloc[:,9:13])
        # tackles: Number of players tackles 
        # tackles_won: Tackles in which the tacklers team won possession of the ball after 
        # tackles_def_third: Tackles in the defensive third of the pitch 
        # tackles_mid_third: Tackles in the middle third of the pitch
        # tackles_att_third: Tackles in the attacking third of the pitch
        df.rename(columns={'Tkl': 'tackles', 'TklW': 'tackles_won', 'Def 3rd': 'tackles_def_third', 'Mid 3rd': 'tackles_mid_third', 'Att 3rd': 'tackles_att_third'}, inplace=True)
        
        df = df.join(df_defense.iloc[:,13:24])
        # drib_tackles: Number of dribblers tackled 
        # drib_attempted: Number of unsuccessful challenges plus number of dribblers tackled 
        # per_drib_tackled: Percentage of dribblers tackled (number of dribblers tackled divided by the number of attempts to challenge an oppossing dribbler)
        # drib_lost: Number of unsuccessful attempts to challenge a dribbling player 
        # blocks: Number of times blocking the ball by standing in its path 
        # shot_blocks : Number of times blocking a shot by standing in its path
        # pass_blocks: Number of times blocking a pass by standing in its path 
        # interceptions: Interceptions
        # tackles_interceptions: Number of players tackled plus interceptions 
        # clearances: Clearances 
        # shot_errors: Mistakes leading to an opponents shots
        df.rename(columns={'Tkl': 'drib_tackles', 'Att': 'drib_attempted', 'Tkl%': 'per_drib_tackled', 'Lost': 'drib_lost', 'Blocks': 'blocks', 'Sh': 'shot_blocks', 'Pass': 'pass_blocks', 'Int': 'interceptions', 'Tkl+Int': 'tackles_interceptions', 'Clr': 'clearances', 'Err': 'shot_errors'}, inplace=True)

        df = df.join(df_poss.iloc[:,8:30])
        # touches: Number of times a player touched the ball 
        # touches_def_pen: Touches in the defensive penalty area
        # touches_def_third: Number of touches in the defensive third 
        # touches_mid_third: Number of touches in the middle third
        # touches_att_third: Number of touches in the attacking third 
        # touches_att_pen: Number of touches in the opposing penalty area 
        # live_touches: Live-ball touches 
        # take_ons_attempted: Number of attempts to take on opposing players while dribbling 
        # take_ons_success: Successful take ons 
        # per_take_ons_success: Percentage of successful take ons from total take ons attempted 
        # take_ons_tackled: Number of times tackled during taking on a player (failed take ons)
        # per_tack_ons_tackled: Percentage of take ons that were tackled (percentage of failed take ons)
        # carries: Number of times a player controlled the ball with their feet 
        # dist_carries: Total disctance a player traveled (in yards) while carrying the ball
        # prog_dist_carries: Progressive distance (yards to the oppositions goal) a player traveled while carrying the ball
        # prog_carries: Number of carries that move the ball closer to the oppositions goal by at least 10 yards or carries into the opposing penalty area. Excludes carries that end in the defending half of the pitch.
        # carries_att_third: Carries that enter the final third closest to the oppositions goal
        # carries_att_pen: Carries into the oppositions penalty area
        # miscontrols: Number of times a player failed when trying to gain control of the ball 
        # dispossessions: Number of times a player gives up the ball after being tackled by an opposing player
        # pass_rec: Number of times a player successfully receives a pass 
        # prog_pass_rec: Number of progressive passes received 
        df = df.rename(columns={'Touches': 'touches', 'Def Pen': 'touches_def_pen', 'Def 3rd': 'touches_def_third', 'Mid 3rd': 'touches_mid_third', 'Att 3rd': 'touches_att_third', 'Att Pen': 'touches_att_pen', 'Live': 'live_touches', 'Succ': 'take_ons_success', 'Att': 'take_ons_attempted', 'Succ%': 'per_take_ons_success', 
                                'Tkld':'take_ons_tackled', 'Tkld%':'per_take_ons_tackled', 'Carries':'carries', 'TotDist':'dist_carries', 'PrgDist':'prog_dist_carries', 'PrgC':'prog_carries', '1/3':'carries_att_third', 'CPA':'carries_att_pen', 'Mis': 'miscontrols', 'Dis': 'dispossessions', 'Rec': 'pass_rec', 'PrgR':'prog_pass_rec'})


        # Make sure to drop all blank rows (FBRef's tables have several)
        df.dropna(subset = ["player"], inplace=True)


        # Turn the minutes columns to integers. So from '1,500' to '1500'. Otherwise it can't do calculations with minutes
        for i in range(0,len(df)):
            df.iloc[i][9] = df.iloc[i][9].replace(',','')
        df.iloc[:,9:] = df.iloc[:,9:].apply(pd.to_numeric)

        # Save the file to the root location
        df.to_csv("%s%s.csv" %(root, raw_nongk), index=False, encoding = 'utf-8-sig')


        ##################################################################################
        ############################## GK SECTION ########################################
        ##################################################################################

        gk = "https://fbref.com/en/comps/%i/keepers/players/%s-Stats" %(lg_id, lg_str)
        advgk = "https://fbref.com/en/comps/%i/keepersadv/players/%s-Stats" %(lg_id, lg_str)

        df_gk = get_players_df(gk)
        df_advgk = get_players_df(advgk)

        df_gk.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
        df_advgk.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)

        df_gk = df_gk.reset_index(drop=True)
        df_advgk = df_advgk.reset_index(drop=True)

        ###############################################################################

        df = pd.read_csv("%s%s.csv" %(root, raw_nongk))
        df = df[df['position'].str.contains("GK")].reset_index().iloc[:,1:]
        df_gk['Pos'] = df_gk['Pos'].astype(str)
        df_gk = df_gk[df_gk['Pos'].str.contains('GK')]
        df_gk = df_gk.reset_index().iloc[:,1:]
        df_gk = df_gk.rename(columns={'PKatt':'PKsFaced'})

        df = df.join(df_gk.iloc[:, 11:26].astype(float), lsuffix='.1', rsuffix='.2')
        df = df.rename(columns={'Player':'player', 'Nation':'nation', 'Squad': 'club', 'Comp': 'comp', 'Age': 'age', 'Born':'year', 'MP': 'matches', 'Starts': 'starts', 'Min': 'minutes',
                                  'SoTA':'shots_ota', 'Saves':'saves', 'Save%.1':'per_saves', 'W':'wins', 'D':'draws', 'L':'losses', 'CS':'clean_sheets', 'CS%':'per_clean_sheets', 'PKatt':'pk_faced',
                                  'PKA': 'pk_allowed', 'PKsv': 'pk_saved', 'PKm':'pk_missed', 'Save%.2':'per_pk_saves'})

        df_advgk['Pos'] = df_advgk['Pos'].astype(str)
        df_advgk = df_advgk[df_advgk['Pos'].str.contains('GK')]
        df_advgk = df_advgk.reset_index().iloc[:,1:]
        df = df.join(df_advgk.iloc[:,9:20].astype(float).rename(columns={'PKA': 'pk_gc', 'FK': 'fk_gc', 'CK': 'ck_gc', 'OG': 'OG_c', 'PSxG': 'post_shot_xg', 'PSxG/SoT': 'post_shot_xg_per_shot_t', 'PSxG+/-': 'post_shot_xg_plus_minus', '/90': 'post_shot_xg_plus_minus_90', 'Cmp': 'launched_pass_cmp', 'Att': 'launched_pass_att', 'Cmp%': 'per_launch_pass_cmp'}))
        df = df.join(df_advgk.iloc[:,20:24].astype(float).rename(columns={'Att (GK)': 'pass_att_gk', 'Thr': 'pass_thow', 'Launch%': 'per_pass_launched', 'AvgLen': 'avg_len'}))
        df = df.join(df_advgk.iloc[:,24:33].astype(float).rename(columns={'Att': 'gk_att', 'Launch%': 'per_gk_launched', 'AvgLen': 'gk_avg_len', 'Opp': 'opp_crosses', 'Stp': 'stop_crosses', 'Stp%': 'per_stop_crosses', '#OPA': 'def_actions_opa', '#OPA/90': 'def_actions_opa_90', 'AvgDist': 'avg_dist_def_actions'}))

        df.to_csv("%s%s.csv" %(root,raw_gk), index=False, encoding = 'utf-8-sig')
        
        
        ##################################################################################
        ##################### Final file for outfield data ###############################
        ##################################################################################

        df = pd.read_csv("%s%s.csv" %(root, raw_nongk))
        df_90s = pd.read_csv("%s%s.csv" %(root, raw_nongk))
        df_90s['90s'] = df_90s['minutes']/90

        for i in range(11,118):
            df_90s.iloc[:,i] = df_90s.iloc[:,i]/df_90s['90s']

        df_90s = df_90s.iloc[:,11:].add_suffix('Per90')
        df_new = df.join(df_90s)

        try:
            for i in range(len(df_new)):
                df_new['Age'][i] = int(df_new['Age'][i][:2])
        except:
            pass


        df_new.to_csv("%s%s.csv" %(root, final_nongk), index=False, encoding = 'utf-8-sig')


        ##################################################################################
        ##################### Final file for keeper data #################################
        ##################################################################################

        df = pd.read_csv("%s%s.csv" %(root, raw_gk))
        df_90s = pd.read_csv("%s%s.csv" %(root, raw_gk))
        df_90s['90s'] = df_90s['minutes']/90
        for i in range(11,157):
            df_90s.iloc[:,i] = df_90s.iloc[:,i]/df_90s['90s']
        df_90s = df_90s.iloc[:,11:].add_suffix('Per90')
        df_new = df.join(df_90s)

        try:
            for i in range(len(df_new)):
                df_new['Age'][i] = int(df_new['Age'][i][:2])
        except:
            pass
            
        df_new.to_csv("%s%s.csv" %(root, final_gk), index=False, encoding = 'utf-8-sig')


        ##################################################################################
        ################ Download team data, for possession-adjusting ####################
        ##################################################################################

        standard = "https://fbref.com/en/comps/%i/stats/squads/%s-Stats" %(lg_id, lg_str)
        poss = "https://fbref.com/en/comps/%i/possession/squads/%s-Stats" %(lg_id, lg_str)

        df_standard = get_team_df(standard)
        df_poss = get_team_df(poss)

        df_standard = df_standard.reset_index(drop=True)
        df_poss = df_poss.reset_index(drop=True)

        ############################################

        df = df_standard.iloc[:, 0:30]

        # Gets the number of touches a team has per 90
        df['TeamTouches90'] = float(0.0)
        for i in range(len(df)):
            df.iloc[i,30] = float(df_poss.iloc[i,5]) / float(df_poss.iloc[i,4])

        # Take out the comma in minutes like above
        for j in range(0,len(df)):
            df.at[j,'Min'] = df.at[j,'Min'].replace(',','')
        df.iloc[:,7:] = df.iloc[:,7:].apply(pd.to_numeric)
        df.to_csv("%s%s TEAMS.csv" %(root, final_nongk), index=False, encoding = 'utf-8-sig')


        ##################################################################################
        ################ Download opposition data, for possession-adjusting ##############
        ##################################################################################

        opp_poss = "https://fbref.com/en/comps/%i/possession/squads/%s-Stats" %(lg_id, lg_str)

        df_opp_poss = get_opp_df(opp_poss)
        df_opp_poss = df_opp_poss.reset_index(drop=True)

        ############################################

        df = df_opp_poss.iloc[:, 0:15]
        df = df.rename(columns={'Touches':'Opp Touches'})
        df = df.reset_index()

        #############################################

        df1 = pd.read_csv("%s%s TEAMS.csv"%(root, final_nongk))

        df1['Opp Touches'] = 1
        for i in range(len(df1)):
            df1['Opp Touches'][i] = df['Opp Touches'][i]
        df1 = df1.rename(columns={'Min':'Team Min'})
        df1.to_csv("%s%s TEAMS.csv" %(root, final_nongk), index=False, encoding = 'utf-8-sig')


        ##################################################################################
        ################ Make the final, complete, outfield data file ####################
        ##################################################################################

        df = pd.read_csv("%s%s.csv" %(root, final_nongk))
        teams = pd.read_csv("%s%s TEAMS.csv" %(root, final_nongk))

        df['AvgTeamPoss'] = float(0.0)
        df['OppTouches'] = int(1)
        df['TeamMins'] = int(1)
        df['TeamTouches90'] = float(0.0)

        player_list = list(df['player'])

        for i in range(len(player_list)):
            team_name = df[df['player']==player_list[i]]['club'].values[0]
            team_poss = teams[teams['Squad']==team_name]['Poss'].values[0]
            opp_touch = teams[teams['Squad']==team_name]['Opp Touches'].values[0]
            team_mins = teams[teams['Squad']==team_name]['Team Min'].values[0]
            team_touches = teams[teams['Squad']==team_name]['TeamTouches90'].values[0]
            df.at[i, 'AvgTeamPoss'] = team_poss
            df.at[i, 'OppTouches'] = opp_touch
            df.at[i, 'TeamMins'] = team_mins
            df.at[i, 'TeamTouches90'] = team_touches

        df.iloc[:,9:] = df.iloc[:,9:].astype(float)
        df.carries = df.carries.astype(float)
        df.touches = df.touches.astype(float)

        # All of these are the possession-adjusted columns. A couple touch-adjusted ones at the bottom
        df['pAdj_tackles_interceptionsPer90'] = (df['tackles_interceptionsPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdj_clearancesPer90'] = (df['clearancesPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdj_shot_blocksPer90'] = (df['shot_blocksPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdj_pass_blocksPer90'] = (df['pass_blocksPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdj_interceptionsPer90'] = (df['interceptionsPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdj_drib_tacklesPer90'] = (df['drib_tacklesPer90']/(100-df['AvgTeamPoss']))*50
        #df['pAdj_tackles_win_possessionPer90'] = (df['drib_tacklesPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdj_drib_lostPer90'] = (df['drib_lostPer90']/(100-df['AvgTeamPoss']))*50
        #df['pAdjAerialWinsPer90'] = (df['AerialWinsPer90']/(100-df['AvgTeamPoss']))*50
        #df['pAdjAerialLossPer90'] = (df['AerialLossPer90']/(100-df['AvgTeamPoss']))*50
        #df['pAdjDrbPastAttPer90'] = (df['DrbPastAttPer90']/(100-df['AvgTeamPoss']))*50
        df['touch_centrality'] = (df['touchesPer90']/df['TeamTouches90'])*100
        # df['pAdj#OPAPer90'] =(df['#OPAPer90']/(100-df['AvgTeamPoss']))*50
        df['tackles_interceptionsPer600OppTouch'] = df['tackles_interceptions'] /(df['OppTouches']*(df['minutes']/df['TeamMins']))*600
        df['pAdj_touchesPer90'] = (df['touchesPer90']/(df['AvgTeamPoss']))*50
        df['carriesPer50Touches'] = df.apply(lambda row: row['carries'] / row['touches'] if row['touches'] != 0 else 0, axis=1)
        df['prog_carriesPer50Touches'] = df.apply(lambda row: row['prg_c'] / row['touches'] if row['touches'] != 0 else 0, axis=1)
        df['prog_passesPer50CmpPasses'] = df.apply(lambda row: row['prg_p'] / row['pass_cmp'] if row['pass_cmp'] != 0 else 0, axis=1)


        # Now we'll add the players' actual positions, from @jaseziv, into the file
        tm_pos = pd.read_csv('https://github.com/griffisben/Soccer-Analyses/blob/main/TransfermarktPositions-Jase_Ziv83.csv?raw=true')
        tm_pos.rename(columns={'Player': 'player'}, inplace=True)
        df = pd.merge(df, tm_pos, on ='player', how ='left')

        for i in range(len(df)):
            if df.position[i] == 'GK':
                df['Main Position'][i] = 'Goalkeeper'
        df.to_csv("%s%s.csv" %(root, final_nongk), index=False, encoding='utf-8-sig')


        ##################################################################################
        ################ Make the final, complete, keepers data file #####################
        ##################################################################################

        df = pd.read_csv("%s%s.csv" %(root, final_gk))
        teams = pd.read_csv("%s%s TEAMS.csv" %(root, final_nongk))

        df['AvgTeamPoss'] = float(0.0)
        df['OppTouches'] = float(0.0)
        df['TeamMins'] = float(0.0)
        df['TeamTouches90'] = float(0.0)

        player_list = list(df['player'])

        for i in range(len(player_list)):
            team_name = df[df['player']==player_list[i]]['club'].values[0]
            team_poss = teams[teams['Squad']==team_name]['Poss'].values[0]
            opp_touch = teams[teams['Squad']==team_name]['Opp Touches'].values[0]
            team_mins = teams[teams['Squad']==team_name]['Team Min'].values[0]
            team_touches = teams[teams['Squad']==team_name]['TeamTouches90'].values[0]
            df.at[i, 'AvgTeamPoss'] = team_poss
            df.at[i, 'OppTouches'] = opp_touch
            df.at[i, 'TeamMins'] = team_mins
            df.at[i, 'TeamTouches90'] = team_touches

        df.iloc[:,9:] = df.iloc[:,9:].astype(float)
        df.carries = df.carries.astype(float)
        df.touches = df.touches.astype(float)

        # Same thing, makes pAdj stats for the GK file
        df['pAdj_tackles_interceptionsPer90'] = (df['tackles_interceptionsPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdj_clearancesPer90'] = (df['clearancesPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdj_shot_blocksPer90'] = (df['shot_blocksPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdj_pass_blocksPer90'] = (df['pass_blocksPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdj_interceptionsPer90'] = (df['interceptionsPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdj_drib_tacklesPer90'] = (df['drib_tacklesPer90']/(100-df['AvgTeamPoss']))*50
        #df['pAdjTklWinPossPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
        df['pAdj_drib_lostPer90'] = (df['drib_lostPer90']/(100-df['AvgTeamPoss']))*50
        #df['pAdjAerialWinsPer90'] = (df['AerialWinsPer90']/(100-df['AvgTeamPoss']))*50
        #df['pAdjAerialLossPer90'] = (df['AerialLossPer90']/(100-df['AvgTeamPoss']))*50
        #df['pAdjDrbPastAttPer90'] = (df['DrbPastAttPer90']/(100-df['AvgTeamPoss']))*50
        df['touch_centrality'] = (df['touchesPer90']/df['TeamTouches90'])*100
        #df['pAdj#OPAPer90'] =(df['#OPAPer90']/(100-df['AvgTeamPoss']))*50
        df['tackles_interceptionsPer600OppTouch'] = df['tackles_interceptions'] /(df['OppTouches']*(df['minutes']/df['TeamMins']))*600
        df['pAdj_touchesPer90'] = (df['touchesPer90']/(df['AvgTeamPoss']))*50
        df['carriesPer50Touches'] = df.apply(lambda row: row['carries'] / row['touches'] if row['touches'] != 0 else 0, axis=1)
        df['prog_carriesPer50Touches'] = df.apply(lambda row: row['prg_c'] / row['touches'] if row['touches'] != 0 else 0, axis=1)
        df['prog_passesPer50CmpPasses'] = df.apply(lambda row: row['prg_p'] / row['pass_cmp'] if row['pass_cmp'] != 0 else 0, axis=1)


        # Just adding the main positions to the GK too, but of course, they will all be GK lol. Keeps other program variables clean
        tm_pos = pd.read_csv('https://github.com/griffisben/Soccer-Analyses/blob/main/TransfermarktPositions-Jase_Ziv83.csv?raw=true')
        tm_pos.rename(columns={'Player': 'player'}, inplace=True)
        df = pd.merge(df, tm_pos, on ='player', how ='left')

        for i in range(len(df)):
            if df.position[i] == 'GK':
                df['Main Position'][i] = 'Goalkeeper'
        df.to_csv("%s%s.csv" %(root, final_gk), index=False, encoding='utf-8-sig')

        os.remove(f'{root}{raw_gk}.csv')
        os.remove(f'{root}{raw_nongk}.csv')
        os.remove(f'{root}{final_nongk} TEAMS.csv')
        
scrape_fbref_next12_leagues_players(comps=comps_next7, seasons=ssns)
        
        
for comp, postgres in comps_postgres_next7.items():
    
    season = comps_seasons_next7[comp]
    
    data = pd.read_csv(os.path.join(
        root,
        f"Final FBRef {season} - {comp}.csv"))
    
    data.drop(columns=['90s'], inplace=True)
    
    data = data.loc[:, ~data.columns.duplicated()]
    data = data.drop_duplicates()
    
    create_table_fbref_outfield(data=data, comp=comp, season=season, postgres=postgres, date=date_today)
    
    os.remove(os.path.join(
        root,
        f"Final FBRef {season} - {comp}.csv"))
    
    data = pd.read_csv(os.path.join(
        root,
        f"Final FBRef GK {season} - {comp}.csv"))
    
    data = data.loc[:, ~data.columns.duplicated()]
    data = data.drop_duplicates()
    
    data.drop(columns=['position', '90s', 'goals', 'assists', 'g_a', 'np_goals', 'pk', 'pk_att', 'prg_c', 'prg_p', 'prg_r',
                       'shots', 'shots_t', 'per_shots_t', 'shots_90', 'shots_t_90', 'g_shots', 'g_shots_t', 'fk_shots',
                       'xG', 'npxG', 'npxg_shots', 'g_minus_xg', 'npg_minus_npxg', 'xag', 'a_minus_xag', 'thru_balls',
                       'throw_ins', 'ck', 'inswing_ck', 'outswing_ck', 'straight_ck', 'sca_take_on', 'sca_shot', 'sca_fouls',
                       'sca_def_actions', 'gc_actions', 'gc_actions_90', 'gca_live_pass', 'gca_dead_pass', 'gca_take_on',
                       'gca_shot', 'gca_fouls', 'gca_def_actions', 'tackles_won', 'tackles_def_third', 'tackles_mid_third',
                       'tackles_att_third', 'drib_tackles', 'drib_attempted', 'per_drib_tackled', 'drib_lost', 'blocks',
                       'shot_blocks', 'pass_blocks', 'interceptions', 'tackles_interceptions', 'shot_errors',
                       'touches_att_third', 'touches_att_pen', 'take_ons_attempted', 'take_ons_success', 'per_take_ons_success',
                       'take_ons_tackled', 'per_take_ons_tackled', 'prog_carries', 'carries_att_third', 'carries_att_pen',
                       'prog_pass_rec', 
                       'goalsPer90', 'assistsPer90', 'g_aPer90', 'np_goalsPer90', 'pkPer90', 'pk_attPer90', 'prg_cPer90', 'prg_pPer90', 'prg_rPer90',
                       'shotsPer90', 'shots_tPer90', 'per_shots_tPer90', 'shots_90Per90', 'shots_t_90Per90', 'g_shotsPer90', 'g_shots_tPer90', 'fk_shotsPer90',
                       'xGPer90', 'npxGPer90', 'npxg_shotsPer90', 'g_minus_xgPer90', 'npg_minus_npxgPer90', 'xagPer90', 'a_minus_xagPer90', 'thru_ballsPer90',
                       'throw_insPer90', 'ckPer90', 'inswing_ckPer90', 'outswing_ckPer90', 'straight_ckPer90', 'sca_take_onPer90', 'sca_shotPer90', 'sca_foulsPer90',
                       'sca_def_actionsPer90', 'gc_actionsPer90', 'gc_actions_90Per90', 'gca_live_passPer90', 'gca_dead_passPer90', 'gca_take_onPer90',
                       'gca_shotPer90', 'gca_foulsPer90', 'gca_def_actionsPer90', 'tackles_wonPer90', 'tackles_def_thirdPer90', 'tackles_mid_thirdPer90',
                       'tackles_att_thirdPer90', 'drib_tacklesPer90', 'drib_attemptedPer90', 'per_drib_tackledPer90', 'drib_lostPer90', 'blocksPer90',
                       'shot_blocksPer90', 'pass_blocksPer90', 'interceptionsPer90', 'tackles_interceptionsPer90', 'shot_errorsPer90',
                       'touches_att_thirdPer90', 'touches_att_penPer90', 'take_ons_attemptedPer90', 'take_ons_successPer90', 'per_take_ons_successPer90',
                       'take_ons_tackledPer90', 'per_take_ons_tackledPer90', 'prog_carriesPer90', 'carries_att_thirdPer90', 'carries_att_penPer90',
                       'prog_pass_recPer90'], inplace=True)
    
    create_table_fbref_goalkeeper(data=data, comp=comp, season=season, postgres=postgres, date=date_today)
    
    os.remove(os.path.join(
        root,
        f"Final FBRef GK {season} - {comp}.csv"))


