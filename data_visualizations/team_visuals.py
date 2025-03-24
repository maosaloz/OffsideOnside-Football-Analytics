import pandas as pd 
import os 
import numpy as np
from utilities import all_teams, away_games, engine, base_path, logo_path, logo, title_font, label_font


import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from mplsoccer import VerticalPitch, FontManager
from mplsoccer import Pitch
from scipy.ndimage import gaussian_filter
from PIL import Image
import matplotlib
from matplotlib.colors import to_rgba
from matplotlib.colors import Normalize

data = pd.read_sql("SELECT * FROM whoscored.juventus", 
                      engine)


def griffis_match_report(data, home_team, away_team, score, league, gameweek):
    
    end_color_h = '#FF4500' 
    end_color_a = '#1A78CF'
    
    df_base = data[(data['team_name']==home_team)&(data['opponent_name']==away_team)|
                   (data['team_name']==away_team)&(data['opponent_name']==home_team)]
    df_base = df_base[(df_base['score']==score)]
    
    df_base = df_base[df_base['half']!=5].reset_index(drop=True)
    
    df_base.rename(columns={                             # Don't need this once Issue 7 is fixed
        'spec1': 'spec_name1',
        'spec1_value': 'spec_value1',
        'spec1': 'spec_name2',
        'spec1_value': 'spec_value2',
        'spec1': 'spec_name3',
        'spec1_value': 'spec_value3',
        'spec1': 'spec_name4',
        'spec1_value': 'spec_value4',
        'spec1': 'spec_name5',
        'spec1_value': 'spec_value5',
        'spec1': 'spec_name6',
        'spec1_value': 'spec_value6'}, inplace=True)

    type_cols = [col for col in df_base.columns if 'spec_name' in col]                                      # Creating columns for specifications 
    df_base['Cross'] = df_base[type_cols].apply(lambda row: 1 if 'Cross' in row.values else 0, axis=1)
    df_base['Corner'] = df_base[type_cols].apply(lambda row: 1 if 'CornerTaken' in row.values else 0, axis=1)
    df_base['KeyPass'] = df_base[type_cols].apply(lambda row: 1 if 'KeyPass' in row.values else 0, axis=1)
    df_base['ShotAssist'] = df_base[type_cols].apply(lambda row: 1 if 'ShotAssist' in row.values else 0, axis=1)
    df_base['FK'] = df_base[type_cols].apply(lambda row: 1 if 'FreeKickTaken' in row.values else 0, axis=1)
    df_base['IFK'] = df_base[type_cols].apply(lambda row: 1 if 'IndirectFreeKickTaken' in row.values else 0, axis=1)
    df_base['GK'] = df_base[type_cols].apply(lambda row: 1 if 'GoalKick' in row.values else 0, axis=1)
    df_base['ThrowIn'] = df_base[type_cols].apply(lambda row: 1 if 'ThrowIn' in row.values else 0, axis=1)
    df_base['RedCard'] = df_base[type_cols].apply(lambda row: 1 if any(val in ['SecondYellow', 'Red'] for val in row.values) else 0, axis=1)
    
    df = df_base.copy()
    df = df[(df['Corner']==0) & (df['FK']==0) & (df['IFK']==0) & (df['GK']==0) & (df['ThrowIn']==0)]
    df = df[(df['action']=='Pass') & (df['outcome']=='Successful')]                     # Only keeping successful passes

    xT = pd.read_csv('https://raw.githubusercontent.com/mckayjohns/youtube-videos/main/data/xT_Grid.csv', header=None)
    xT = np.array(xT)
    xT_rows, xT_cols = xT.shape

    df['x1_bin_xT'] = pd.cut(df['x'], bins=xT_cols, labels=False)                       # Cutting the pitch into bins 
    df['y1_bin_xT'] = pd.cut(df['y'], bins=xT_rows, labels=False)
    df['x2_bin_xT'] = pd.cut(df['endx'], bins=xT_cols, labels=False)
    df['y2_bin_xT'] = pd.cut(df['endy'], bins=xT_rows, labels=False)

    df['start_zone_value_xT'] = df[['x1_bin_xT', 'y1_bin_xT']].apply(lambda x: xT[x[1]][x[0]], axis=1)
    df['end_zone_value_xT'] = df[['x2_bin_xT', 'y2_bin_xT']].apply(lambda x: xT[x[1]][x[0]], axis=1)

    df['xT'] = df['end_zone_value_xT'] - df['start_zone_value_xT']

    colors = np.arctan2(df['xT'],[.01]*len(df))
    
    norm = Normalize()
    norm.autoscale(colors)
    
    
    
    

    ##########################################################################################
    #       TITLE: HOME xT BY ZONE START
    ##########################################################################################
    pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2)
  
    bins = (36, 19)

    maxstat = pitch.bin_statistic(df.x, df.y,
                                  df.xT, statistic='sum', bins=bins,)
    maxstatend = pitch.bin_statistic(df.endx, df.endy,
                                     df.xT, statistic='sum', bins=bins,)

    dfh = df[df['team_name']==home_team].reset_index(drop=True)

    pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2)
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('#fbf9f4')

    my_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#F7FFFF',end_color_h])
    # blank_hmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#fbf9f4','#fbf9f4'])

    bins = (36, 19)
    bs_heatmap = pitch.bin_statistic(df[df['team_name']==home_team].x, df[df['team_name']==home_team].y,
                                     values=df[df['team_name']==home_team].xT, statistic='sum', bins=bins,)
    bs_heatmap['statistic'] = gaussian_filter(bs_heatmap['statistic'], 1)

    ####################################################

    hm = pitch.heatmap(bs_heatmap, ax=ax, cmap=my_cmap, edgecolor='#F7FFFF', vmin=0, lw=.1,
                       vmax=np.percentile(maxstat['statistic'],95), alpha=0.8
                       )
    
    

    ax.text(0, 102, "{} Passing xT\nStart Zone".format(home_team.capitalize()),
            color='#4A2E19',
            va='bottom', 
            ha='left',
            fontdict=title_font)

    ax.text(50,-2, 'Direction of Attack --->',
            color='#4A2E19',
            va='top', 
            ha='center',
            fontdict=label_font)

    fig=plt.gcf()
    fig.set_size_inches(10, 7) #length, height
    fig.patch.set_facecolor('#F7FFFF')
    
    newax = fig.add_axes([.77, .87, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{home_team} xT By Zone Start.png"), 
        dpi = 300)
    plt.clf()
    
    
    
    
    
    
    ##########################################################################################
    #       TITLE: HOME xT BY ZONE END
    ##########################################################################################
    
    dfh = df[df['team_name']==home_team].copy().reset_index(drop=True)

    pitch = VerticalPitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2, half=True)
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('#F7FFFF')

    my_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#F7FFFF',end_color_h])

    bins = (36, 19)
    bs_heatmap = pitch.bin_statistic(df[df['team_name']==home_team].endx, df[df['team_name']==home_team].endy,
                                     values=df[df['team_name']==home_team].xT, statistic='sum', bins=bins,)
    bs_heatmap['statistic'] = gaussian_filter(bs_heatmap['statistic'], 1)

    ####################################################

    hm = pitch.heatmap(bs_heatmap, ax=ax, cmap=my_cmap, edgecolor='#F7FFFF', vmin=0, lw=.1,
                       vmax=np.percentile(maxstatend['statistic'],95), alpha=0.8
                       )

    ax.text(100, 102, "{} Passing xT\nEnd Zone".format(home_team.capitalize()),
            color='#4A2E19',
            va='bottom', 
            ha='left',
            fontdict=title_font)

    fig=plt.gcf()
    fig.set_size_inches(10, 7) #length, height
    fig.patch.set_facecolor('#F7FFFF')
    
    newax = fig.add_axes([.7, .87, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{home_team} xT By Zone End.png"), 
        dpi = 300)

    plt.clf()
    
    
    
    
    
    
    ##########################################################################################
    #            TITLE: AWAY xT BY ZONE START
    ##########################################################################################
    
    dfh = df[df['team_name']==away_team].copy().reset_index(drop=True)

    pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2, half=False)
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('#F7FFFF')
    
    my_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#F7FFFF',end_color_a])
        # blank_hmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#fbf9f4','#fbf9f4'])

    bins = (36, 19)
    bs_heatmap = pitch.bin_statistic(dfh[dfh['team_name']==away_team].x, dfh[dfh['team_name']==away_team].y,
                                     values=dfh[dfh['team_name']==away_team].xT, statistic='sum', bins=bins,)
    bs_heatmap['statistic'] = gaussian_filter(bs_heatmap['statistic'], 1)
    
    ####################################################

    hm = pitch.heatmap(bs_heatmap, ax=ax, cmap=my_cmap, edgecolor='#F7FFFF', vmin=0, lw=.1,
                       vmax=np.percentile(maxstat['statistic'],95), alpha=0.8
                       )

    ax.text(0, 102, "{} Passing xT\nStart Zone".format(away_team.capitalize()),
            color='#4A2E19',
            va='bottom', 
            ha='left',
            fontdict=title_font)

    ax.text(50,-2, 'Direction of Attack --->',
            color='#4A2E19',
            va='top', 
            ha='center',
            fontdict=label_font)

    fig=plt.gcf()
    fig.set_size_inches(10, 7) #length, height
    fig.patch.set_facecolor('#F7FFFF')
    
    newax = fig.add_axes([.77, .87, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{away_team} xT By Zone Start.png"), 
        dpi = 300)
    
    plt.clf()







    ##########################################################################################
    #            TITLE: Away xT BY ZONE END
    ##########################################################################################
    dfh = df[df['team_name']==away_team].copy().reset_index(drop=True)

    pitch = VerticalPitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=5, half=True)
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('#fbf9f4')

    my_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#F7FFFF',end_color_a])
        # blank_hmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#fbf9f4','#fbf9f4'])
    
    bins = (36, 19)
    bs_heatmap = pitch.bin_statistic(df[df['team_name']==away_team].endx, df[df['team_name']==away_team].endy,
                                     values=df[df['team_name']==away_team].xT, statistic='sum', bins=bins,)
    bs_heatmap['statistic'] = gaussian_filter(bs_heatmap['statistic'], 1)

    ####################################################

    hm = pitch.heatmap(bs_heatmap, ax=ax, cmap=my_cmap, edgecolor='#F7FFFF', vmin=0, lw=.1,
                       vmax=np.percentile(maxstatend['statistic'],95), alpha=0.8
                       )

    ax.text(100, 102, "{} Passing xT\nEnd Zone".format(home_team.capitalize()),
            color='#4A2E19',
            va='bottom', 
            ha='left',
            fontdict=title_font)

    fig=plt.gcf()
    fig.set_size_inches(10, 7) #length, height
    fig.patch.set_facecolor('#F7FFFF')

    newax = fig.add_axes([.7, .87, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{away_team} xT By Zone End.png"), 
        dpi = 300)

    plt.clf()

    




    ##########################################################################################
    #                TITLE: HOME FINAL THIRD PASSES
    ##########################################################################################
    
    
    df = df_base.copy()
    df = df[df['action']=='Pass']
        
    dfh = df[df['team_name']==home_team].copy().reset_index(drop=True)

    df_final3_cmp = dfh[(dfh['action']=='Pass') &
                         (dfh['outcome']=='Successful') &
                         (dfh['endx']>=100-(100/3)) &
                         (dfh['x']<=100-(100/3))]
    df_final3_inc = dfh[(dfh['action']=='Pass') &
                           (dfh['outcome']=='Unsuccessful') &
                           (dfh['endx']>=100-(100/3)) &
                           (dfh['x']<=100-(100/3))]

    pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2, half=False)
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('#F7FFFF')

    incpass = pitch.lines(df_final3_inc.x,
                          df_final3_inc.y,
                          df_final3_inc.endx,
                          df_final3_inc.endy,
                             comet=True, alpha=.3,
                          lw=1.5, label='Incomplete',
                          color='silver', ax=ax)
    cmppass = pitch.lines(df_final3_cmp.x,
                          df_final3_cmp.y,
                          df_final3_cmp.endx,
                          df_final3_cmp.endy,
                              comet=True, alpha=.3,
                          lw=4, label='Complete',
                          color=end_color_h, ax=ax)

    incdot = pitch.scatter(df_final3_inc.endx, df_final3_inc.endy,
                             s=5, c='silver', zorder=2, ax=ax)
    cmpdot = pitch.scatter(df_final3_cmp.endx, df_final3_cmp.endy,
                             s=20, c=end_color_h, zorder=2, ax=ax)

    ax.text(0, 102, "{} Passing xT\nEnd Zone".format(home_team.capitalize()),
            color='#4A2E19',
            va='bottom', 
            ha='left',
            fontdict=title_font)
    ax.text(50,-2, 'Direction of Attack --->',
            color='#4A2E19',
            va='top', 
            ha='center',
            fontdict=label_font)
    ax.text(99,-2, 'Complete',
            color=end_color_h,
            va='top', 
            ha='right',
            fontdict=label_font)
    ax.text(1,-2, 'Incomplete',
            color='silver',
            va='top', 
            ha='left',
            fontdict=label_font)

    fig=plt.gcf()
    fig.set_size_inches(10, 7) #length, height
    fig.patch.set_facecolor('#F7FFFF')
    
    newax = fig.add_axes([.8, .87, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{home_team} Final Third Passes.png"), 
        dpi = 300)

    plt.clf()
    
    
    
    
    

    ##########################################################################################
    #            TITLE: AWAY FINAL THIRD PASSES
    ##########################################################################################
    dfh = df[df['team_name']==away_team].copy().reset_index(drop=True)

    df_final3_cmp = dfh[(dfh['action']=='Pass') &
                         (dfh['outcome']=='Successful') &
                         (dfh['endx']>=100-(100/3)) &
                         (dfh['x']<=100-(100/3))]
    df_final3_inc = dfh[(dfh['action']=='Pass') &
                           (dfh['outcome']=='Unsuccessful') &
                           (dfh['endx']>=100-(100/3)) &
                           (dfh['x']<=100-(100/3))]

    pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2, half=False)
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('#F7FFFF')

    incpass = pitch.lines(df_final3_inc.x,
                          df_final3_inc.y,
                          df_final3_inc.endx,
                          df_final3_inc.endy,
                              comet=True, alpha=.3,
                          lw=1.5, label='Incomplete',
                          color='silver', ax=ax)
    cmppass = pitch.lines(df_final3_cmp.x,
                          df_final3_cmp.y,
                          df_final3_cmp.endx,
                          df_final3_cmp.endy,
                              comet=True, alpha=.3,
                          lw=4, label='Complete',
                          color=end_color_a, ax=ax)

    incdot = pitch.scatter(df_final3_inc.endx, df_final3_inc.endy,
                           s=5, c='silver', zorder=1, ax=ax)
    cmpdot = pitch.scatter(df_final3_cmp.endx, df_final3_cmp.endy,
                           s=20, c=end_color_a, zorder=1, ax=ax)

    ax.text(0, 102, "{} Passing xT\nEnd Zone".format(away_team.capitalize()),
            color='#4A2E19',
            va='bottom', 
            ha='left',
            fontdict=title_font)
    ax.text(50,-2, 'Direction of Attack --->',
            color='#4A2E19',
            va='top', 
            ha='center',
            fontdict=label_font)
    ax.text(99,-2, 'Complete',
            color=end_color_a,
            va='top', 
            ha='right',
            fontdict=label_font)
    ax.text(1,-2, 'Incomplete',
            color='silver',
            va='top', 
            ha='left',
            fontdict=label_font)

    fig=plt.gcf()
    fig.set_size_inches(10, 7) #length, height
    fig.patch.set_facecolor('#F7FFFF')

    newax = fig.add_axes([.8, .87, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{away_team} Final Third Passes.png"), 
        dpi = 300)

    plt.clf()

    
    

griffis_match_report(data, 
                     home_team = 'juventus', 
                     away_team = 'inter', 
                     score = '1 : 0', 
                     league = 'serie_a', 
                     gameweek = 'gameweek 30')