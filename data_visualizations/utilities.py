#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 10:39:12 2025

@author: Mao
"""

from sqlalchemy import create_engine
import matplotlib.image as mpimg

engine = create_engine("postgresql://postgres:Chachagui1@@localhost:5432/serie_a")

base_path = '/Users/Mao/Documents/Offside:onside'

logo_path = '/Users/Mao/Downloads/offside_onside_logo.png' # adapt
logo = mpimg.imread(logo_path)

title_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 30}
label_font = {'family': 'serif', 'fontname': 'Charter', 'fontsize': 20}

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

def away_games(data, team):
    
    team_id_to_name = {int(v): k for k, v in all_teams.items()}
    
    data['home_team_name'] = data['home_teamid'].map(team_id_to_name)

    mask = data['home_team_name'] != team
    data.loc[mask, 'x'] = 100 - data.loc[mask, 'x']
    data.loc[mask, 'endx'] = 100 - data.loc[mask, 'endx']
    data.loc[mask, 'y'] = 100 - data.loc[mask, 'y']
    data.loc[mask, 'endy'] = 100 - data.loc[mask, 'endy']
    
