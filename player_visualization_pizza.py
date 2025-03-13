#Importing the libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import math
from mplsoccer import PyPizza, add_image, FontManager

# This example comes from the Çalhanoglu article, therefore data cleaning is needed before you're 
# able to create the pizza plot. 

columns_to_move = ['xAG', 'npxG', 'PassLive_Goal', 'PassDead_Goal', 'PassLive_Shot', 'PassDead_Shot']

# Reorder columns to move specified columns to the last positions
df = df[[col for col in df.columns if col not in columns_to_move] + columns_to_move]

params = list(df.columns)
params = params[5:]

df['Player'].unique()

player = df[df['Player']=='Hakan Çalhanoğlu'].reset_index()  # Change to the specified player
player = list(player.loc[0])
player = player[6:]

#Calculating the percentile rank for the player w.r.t each metric
values = []

for x in range(len(params)):
    values.append(math.floor(stats.percentileofscore(df[params[x]],player[x])))

for n,i in enumerate(values):
    if i == 100:
        values[n] = 99
        
#Renaming the parameters for a better reading on the plot
params1 = ['TklW',
           'Tkl vs\nDribbler',
           'Tkl %\nWon',
           'Int',
           'Pass Cmp%',
           'Short Pass\nCmp%',
           'Med Pass\nCmp%',
           'Long Pass\nCmp%',
           'KP',
           'PrgP',
           'Mis',
           'Dis',
           'PrgP_percent',
           'xAG',
           'npxG',
           'Live Pass\nto Goal',
           'Dead Pass\nto Goal',
           'Live Pass\nto Shot', 
           'Dead Pass\nto Shot']


slice_colors = ["#1A78CF"] * 4 + ["#FF9300"] * 9 + ["#D70232"] * 6 #slice colors
text_colors = ["#000000"] * 13 + ["#F2F2F2"] * 6 #slice text colors

# We should change this section to produce an Offside/onside template
# instantiate PyPizza class
baker = PyPizza(
    params=params1,                  # list of parameters
    background_color="#EBEBE9",     # background color
    straight_line_color="#EBEBE9",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_lw=0,               # linewidth of last circle
    other_circle_lw=0,              # linewidth for other circles
    inner_circle_size=20            # size of inner circle
)

# plot pizza
fig, ax = baker.make_pizza(
    values,                          # list of values
    figsize=(8, 8.5),                # adjust figsize according to your need
    color_blank_space="same",        # use same color to fill blank space
    slice_colors=slice_colors,       # color for individual slices
    value_colors=text_colors,        # color for the value-text
    value_bck_colors=slice_colors,   # color for the blank spaces
    blank_alpha=0.4,                 # alpha for blank-space colors
    kwargs_slices=dict(
        edgecolor="#F2F2F2", zorder=2, linewidth=1
    ),                               # values to be used when plotting slices
    kwargs_params=dict(
        color="#000000", fontsize=11,
         va="center"
    ),                               # values to be used when adding parameter
    kwargs_values=dict(
        color="#000000", fontsize=11,
         zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="cornflowerblue",
            boxstyle="round,pad=0.2", lw=1
        )
    )                                # values to be used when adding parameter-values
)

#Title
fig.text(
    0.515, 0.975, "Hakan Çalhanoğlu - Internazionale", size=16,
    ha="center", color="#000000"
)

#Subtitle
fig.text(
    0.515, 0.953,
    "per90 Percentile Rank vs Complete Midfielders | Season 2023-24",
    size=13,
    ha="center",  color="#000000"
)

#Credits
CREDIT_1 = "data: statsbomb viz fbref"
CREDIT_2 = "Visualization: Abhilash U Prakash(@Abhilashprakash)"

fig.text(
    0.99, 0.02, f"{CREDIT_1}\n{CREDIT_2}", size=9,
     color="#000000",
    ha="right"
)

# add text
fig.text(
    0.34, 0.925, "Defend        Possession      Attack", size=14,
     color="#000000"
)

# add rectangles
fig.patches.extend([
    plt.Rectangle(
        (0.31, 0.9225), 0.025, 0.021, fill=True, color="#1a78cf",
        transform=fig.transFigure, figure=fig
    ),
    plt.Rectangle(
        (0.462, 0.9225), 0.025, 0.021, fill=True, color="#ff9300",
        transform=fig.transFigure, figure=fig
    ),
    plt.Rectangle(
        (0.632, 0.9225), 0.025, 0.021, fill=True, color="#d70232",
        transform=fig.transFigure, figure=fig
    ),
])
