#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 18:19:22 2025

@author: Mao
"""

import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine

data_download_loc = '/Users/Mao/Downloads'
chrome_driver_loc = '/Users/Mao/Downloads/chromedriver-mac-arm64 2/chromedriver' 

serieA_teams = {
    #'juventus': '87',
    'inter': '75',
    'ac-milan': '80',
    'napoli': '276',
    'roma': '84',
    'atalanta': '300',
    'lazio': '77',
    'fiorentina': '73',
    'bologna': '71'
    }

laliga_teams = {
    'barcelona': '65',
    'real-madrid': '52',
    'atletico-madrid': '63',
    'villarreal': '839',
    'athletic-club': '53',
    'real-betis': '54',
    'sevilla': '67',
    'real-sociedad': '68'
    }

epl_teams = {
    'liverpool': '26',
    'arsenal': '13',
    'bournemouth': '183',
    'manchester-city': '167',
    'brentford': '189',
    'nottingham-forest': '174',
    'tottenham': '30',
    'everton': '31',
    'chelsea': '15',
    'newcastle': '23',
    'crystal-palace': '162',
    'manchester-united': '32',
    'fulham': '170',
    'brighton': '211',
    'west-ham': '29',
    'aston-villa': '24',
    'wolves': '161',
    'leicester': '14',
    'ipswich': '165',
    'southhampton': '18'}

ligue1_teams = {
    'paris-saint-germain': '304',
    'marseille': '249',
    'monaco': '248',
    'nice': '613',
    'lyon': '228',
    'lille': '607'}

bundesliga_teams = {
    'bayern-munich': '37',
    'bayer-leverkusen': '36',
    'mainz-05': '219',
    'eintracht-frankfurt': '45',
    'rb-leipzig': '7614',
    'borussia-m.gladbach': '134',
    'wolfsburg': '33',
    'borussia-dortmund': '44',
    'vfb-stuttgart': '41'}

all_teams = {
    # Serie A
    'juventus': '87', 
    'inter': '75',
    'ac-milan': '80',
    'napoli': '276',
    'roma': '84',
    'atalanta': '300',
    'lazio': '77',
    'fiorentina': '73',
    'bologna': '71',
    'udinese': '86',
    'torino': '72',
    'genoa': '278',
    'como': '1290',
    'verona': '76',
    'cagliari': '78',
    'lecce': '79',
    'parma-calcio-1913': '24341',
    'empoli': '272',
    'venezia': '85',
    'monza': '269',
    
    # La Liga
    'barcelona': '65',
    'real-madrid': '52',
    'atletico-madrid': '63',
    'villarreal': '839',
    'athletic-club': '53',
    'real-betis': '54',
    'sevilla': '67',
    'real-sociedad': '68',
    'getafe': '819',
    'mallorca': '51',
    'rayo-vallecano': '64',
    'osasuna': '131',
    'leganes': '825',
    'celta-vigo': '62',
    'girona': '2783',
    'deportivo-alaves': '60',
    'espanyol': '70',
    'las-palmas': '838',
    'valencia': '55',
    'real-valladolid': '58',
    
    # Premier League
    'liverpool': '26',
    'arsenal': '13',
    'bournemouth': '183',
    'manchester-city': '167',
    'brentford': '189',
    'nottingham-forest': '174',
    'tottenham': '30',
    'everton': '31',
    'chelsea': '15',
    'newcastle': '23',
    'crystal-palace': '162',
    'manchester-united': '32',
    'fulham': '170',
    'brighton': '211',
    'west-ham': '29',
    'aston-villa': '24',
    'wolves': '161',
    'leicester': '14',
    'ipswich': '165',
    'southhampton': '18',
    
    # Ligue 1
    'paris-saint-germain': '304',
    'marseille': '249',
    'monaco': '248',
    'nice': '613',
    'lyon': '228',
    'lille': '607',
    'strasbourg': '148',
    'auxerre': '308',
    'rennes': '313',
    'brest': '2332',
    'toulouse': '246',
    'lens': '309',
    'nantes': '302',
    'reims': '950',
    'angers': '614',
    'le-havre': '217',
    'saint-etienne': '145',
    'montpellier': '311',
    
    # Bundesliga
    'bayern-munich': '37',
    'bayer-leverkusen': '36',
    'mainz-05': '219',
    'eintracht-frankfurt': '45',
    'rb-leipzig': '7614',
    'borussia-m-gladbach': '134',
    'wolfsburg': '33',
    'borussia-dortmund': '44',
    'vfb-stuttgart': '41',
    'freiburg': '50',
    'augsburg': '1730',
    'hoffenheim': '1211',
    'werder-bremen': '42',
    'st-pauli': '283',
    'union-berlin': '796',
    'fc-heidenheim': '4852',
    'bochum': '109',
    'holstein-kiel': '1206',
    
    # Champions league 
    'psv-eindhoven': '129',
    'benfica': '299',
    'celtic': '103',
    'sporting-cp': '296',
    'dinamo-zagreb': '684',
    'feyenoord': '256',
    'club-brugge': '124',
    'shakhtar-donetsk': '1706',
    'fk-crvena-zvezda': '579',
    'sturm-graz': '390',
    'sparta-prague': '354',
    'slovan-bratislava': '698',
    'bsc-young-boys': '587',
    'salzburg': '361'
    
    }

leagues = {'juventus': 'serie_a',
           'inter': 'serie_a',
           'ac-milan': 'serie_a',
           'napoli': 'serie_a',
           'roma': 'serie_a',
           'atalanta': 'serie_a',
           'lazio': 'serie_a',
           'fiorentina': 'serie_a',
           'bologna': 'serie_a',
           'barcelona': 'la_liga',
           'real-madrid': 'la_liga',
           'atletico-madrid': 'la_liga',
           'villarreal': 'la_liga',
           'athletic-club': 'la_liga',
           'real-betis': 'la_liga',
           'sevilla': 'la_liga',
           'real-sociedad': 'la_liga',
           'liverpool': 'premier_league',
           'arsenal': 'premier_league',
           'bournemouth': 'premier_league',
           'manchester-city': 'premier_league',
           'brentford': 'premier_league',
           'nottingham-forest': 'premier_league',
           'tottenham': 'premier_league',
           'everton': 'premier_league',
           'chelsea': 'premier_league',
           'newcastle': 'premier_league',
           'crystal-palace': 'premier_league',
           'manchester-united': 'premier_league',
           'fulham': 'premier_league',
           'brighton': 'premier_league',
           'west-ham': 'premier_league',
           'aston-villa': 'premier_league',
           'wolves': 'premier_league',
           'leicester': 'premier_league',
           'ipswich': 'premier_league',
           'southhampton': 'premier_league',
           'paris-saint-germain': 'ligue_1',
           'marseille': 'ligue_1',
           'monaco': 'ligue_1',
           'nice': 'ligue_1',
           'lyon': 'ligue_1',
           'lille': 'ligue_1',
           'bayern-munich': 'bundesliga',
           'bayer-leverkusen': 'bundesliga',
           'mainz-05': 'bundesliga',
           'eintracht-frankfurt': 'bundesliga',
           'rb-leipzig': 'bundesliga',
           'borussia-m.gladbach': 'bundesliga',
           'wolfsburg': 'bundesliga',
           'borussia-dortmund': 'bundesliga',
           'vfb-stuttgart': 'bundesliga'
           }


def create_table(data, league, team):

    data.rename(columns={
        'teamId': 'teamid',
        'period/value': 'half',
        'playerId': 'playerid',
        'type/displayName': 'action',
        'outcomeType/displayName': 'outcome',
        'endX': 'endx',
        'endY': 'endy',
        'qualifiers/0/type/displayName': 'spec1',
        'qualifiers/0/value': 'spec1_value',
        'qualifiers/1/type/displayName': 'spec2',
        'qualifiers/1/value': 'spec2_value',
        'qualifiers/2/type/displayName': 'spec3',
        'qualifiers/2/value': 'spec3_value',
        'qualifiers/3/type/displayName': 'spec4',
        'qualifiers/3/value': 'spec4_value',
        'qualifiers/4/type/displayName': 'spec5',
        'qualifiers/4/value': 'spec5_value',
        'qualifiers/5/type/displayName': 'spec6',
        'qualifiers/5/value': 'spec6_value'}, inplace=True)
    
    data = data[['teamid', 'team_name', 'opponentid', 'opponent_name', 'minute', 'half', 'score',
                 'home_teamid', 'playerid', 'player_name', 'action', 'outcome', 'x', 'y', 'endx',
                 'endy', 'spec1', 'spec1_value', 'spec2', 'spec2_value', 'spec3', 'spec3_value',
                 'spec4', 'spec4_value', 'spec5', 'spec5_value', 'spec6', 'spec6_value']]

    conn = psycopg2.connect(host='localhost',
                            dbname=f'{league}',
                            user='postgres',
                            password="Chachagui1@",
                            port=5432)
    cur = conn.cursor()
    cur.execute(f"""CREATE TABLE IF NOT EXISTS whoscored.{team} (
            teamid INT,
            team_name VARCHAR(255),
            opponentid INT,
            opponent_name VARCHAR(255),
            minute INT,
            half INT,
            score VARCHAR(255),
            home_teamid INT,
            playerid INT,
            player_name VARCHAR(255),
            action VARCHAR(255),
            outcome VARCHAR(255),
            x INT,
            y INT,
            endx INT,
            endy INT,
            spec1 VARCHAR(255),
            spec1_value VARCHAR(255),
            spec2 VARCHAR(255),
            spec2_value VARCHAR(255),
            spec3 VARCHAR(255),
            spec3_value VARCHAR(255),
            spec4 VARCHAR(255),
            spec4_value VARCHAR(255),
            spec5 VARCHAR(255),
            spec5_value VARCHAR(255),
            spec6 VARCHAR(255),
            spec6_value VARCHAR(255)
            );
    """)       

    conn.commit()
    
    cur.close()
        
    conn.close()

    engine = create_engine(f"postgresql://postgres:Chachagui1@@localhost:5432/{league}")
    data.to_sql(f"{team}", schema="whoscored", con=engine, if_exists="replace", index=False)


