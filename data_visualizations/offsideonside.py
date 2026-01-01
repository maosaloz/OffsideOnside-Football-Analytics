# create classes for the following positions: goalkeeper, wingback, centerback, defensive_mid, offensive_mid, wingers, strikers
import pandas as pd 
import os 
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:Chachagui1@@localhost:5432/serie_a")

df_who = pd.read_sql("SELECT * FROM whoscored.juventus", con=engine)
df_fbref = pd.read_sql("SELECT * FROM fbref.outfield_2025_25723", con=engine)

df_fbref = df_fbref[df_fbref['player']=='Andrea Cambiaso']
df_who = df_who[df_who['player_name'] == 'Andrea Cambiaso']

