import pandas as pd 
import os 
import numpy as np
from utilities import all_teams, away_games, engine, base_path, logo_path, logo, title_font, label_font, small_font


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
        'spec2': 'spec_name2',
        'spec2_value': 'spec_value2',
        'spec3': 'spec_name3',
        'spec3_value': 'spec_value3',
        'spec4': 'spec_name4',
        'spec4_value': 'spec_value4',
        'spec5': 'spec_name5',
        'spec5_value': 'spec_value5',
        'spec6': 'spec_name6',
        'spec6_value': 'spec_value6'}, inplace=True)

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
    """
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
    """

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
    
    
    
    
    
    ##########################################################################################
    #            TITLE: HOME PENALTY PASSES
    ##########################################################################################
    
    dfh = df[df['team_name']==home_team].copy().reset_index(drop=True)

    df_box = dfh[(dfh['action']=='Pass') &
                 ((dfh['endx']>=100-17) &
                  (dfh['endy'].between(21.5,78.5))) 
                    ]
    df_box_cmp = df_box[df_box['outcome']=='Successful']
    df_box_inc = df_box[df_box['outcome']=='Unsuccessful']

    pitch = VerticalPitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2, half=True)
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('#F7FFFF')

    incpass = pitch.lines(df_box_inc.x,
                          df_box_inc.y,
                          df_box_inc.endx,
                          df_box_inc.endy,
                              comet=True, alpha=.3,
                          lw=1.5, label='Incomplete',
                          color='silver', ax=ax)
    cmppass = pitch.lines(df_box_cmp.x,
                          df_box_cmp.y,
                          df_box_cmp.endx,
                          df_box_cmp.endy,
                              comet=True, alpha=.3,
                          lw=4, label='Complete',
                          color=end_color_h, ax=ax)

    incdot = pitch.scatter(df_box_inc.endx, df_box_inc.endy,
                           s=5, c='silver', zorder=1, ax=ax)
    cmpdot = pitch.scatter(df_box_cmp.endx, df_box_cmp.endy,
                           s=20, c=end_color_h, zorder=1, ax=ax)

    ax.text(100, 102, "{} Passes\nInto Penalty Box".format(home_team.capitalize()),
            color='#4A2E19',
            va='bottom', 
            ha='left',
            fontdict=title_font)

    fig=plt.gcf()
    fig.set_size_inches(10, 7) #length, height
    fig.patch.set_facecolor('#F7FFFF')

    newax = fig.add_axes([.72, .85, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{home_team} Penalty Passes.png"), 
        dpi = 300)

    plt.clf()






    ##########################################################################################
    #           TITLE: AWAY PENALTY PASSES
    ##########################################################################################
    
    dfh = df[df['team_name']==away_team].copy().reset_index(drop=True)
    
    df_box = dfh[(dfh['action']=='Pass') &
                     ((dfh['endx']>=100-17) &
                     (dfh['endy'].between(21.5,78.5))) 
                     ]
    df_box_cmp = df_box[df_box['outcome']=='Successful']
    df_box_inc = df_box[df_box['outcome']=='Unsuccessful']

    pitch = VerticalPitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2, half=True)
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('#F7FFFF')

    incpass = pitch.lines(df_box_inc.x,
                          df_box_inc.y,
                          df_box_inc.endx,
                          df_box_inc.endy,
                              comet=True, alpha=.3,
                          lw=1.5, label='Incomplete',
                          color='silver', ax=ax)
    cmppass = pitch.lines(df_box_cmp.x,
                          df_box_cmp.y,
                          df_box_cmp.endx,
                          df_box_cmp.endy,
                              comet=True, alpha=.3,
                          lw=4, label='Complete',
                          color=end_color_a, ax=ax)

    incdot = pitch.scatter(df_box_inc.endx, df_box_inc.endy,
                           s=5, c='silver', zorder=2, ax=ax)
    cmpdot = pitch.scatter(df_box_cmp.endx, df_box_cmp.endy,
                           s=20, c=end_color_a, zorder=2, ax=ax)

    ax.text(100, 102, "{} Passes\nInto Penalty Box".format(away_team.capitalize()),
            color='#4A2E19',
            va='bottom', 
            ha='left',
            fontdict=title_font)

    fig=plt.gcf()
    fig.set_size_inches(10, 7) #length, height
    fig.patch.set_facecolor('#F7FFFF')

    newax = fig.add_axes([.72, .85, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{away_team} Penalty Passes.png"), 
        dpi = 300)

    plt.clf()
    
    
    
    
    ##########################################################################################
    #                TITLE: HOME PASSES IN THE FINAL THRID
    ##########################################################################################
    
    dfh = df[df['team_name']==home_team].copy().reset_index(drop=True)
    dfh = dfh[dfh['Corner']==0]
    dfh = dfh[dfh['ThrowIn']==0]

    df_final3_cmp = dfh[(dfh['action']=='Pass') &
                           (dfh['outcome']=='Successful') &
                           (dfh['x']>=100-(100/3))]
    df_final3_inc = dfh[(dfh['action']=='Pass') &
                           (dfh['outcome']=='Unsuccessful') &
                           (dfh['x']>=100-(100/3))]

    pitch = VerticalPitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2, half=True)
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

    ax.text(100, 102, "{} Passes\nIn Final Third".format(home_team.capitalize()),
            color='#4A2E19',
            va='bottom', 
            ha='left',
            fontdict=title_font)

    fig=plt.gcf()
    fig.set_size_inches(10, 7) #length, height
    fig.patch.set_facecolor('#F7FFFF')
    
    newax = fig.add_axes([.72, .85, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{home_team} Final Third.png"), 
        dpi = 300)

    plt.clf()





    ##########################################################################################
    #               TITLE: AWAY PASSES IN THE FINAL THIRD
    ##########################################################################################
    
    dfh = df[df['team_name']==away_team].copy().reset_index(drop=True)
    dfh = dfh[dfh['Corner']==0]
    dfh = dfh[dfh['ThrowIn']==0]


    df_final3_cmp = dfh[(dfh['action']=='Pass') &
                           (dfh['outcome']=='Successful') &
                           (dfh['x']>=100-(100/3))]
    df_final3_inc = dfh[(dfh['action']=='Pass') &
                           (dfh['outcome']=='Unsuccessful') &
                           (dfh['x']>=100-(100/3))]

    pitch = VerticalPitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19', line_zorder=2, half=True)
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

    ax.text(100, 102, "{} Passes\nIn Final Third".format(away_team.capitalize()),
            color='#4A2E19',
            va='bottom', 
            ha='left',
            fontdict=title_font)

    fig=plt.gcf()
    fig.set_size_inches(10, 7) #length, height
    fig.patch.set_facecolor('#F7FFFF')
    
    newax = fig.add_axes([.72, .85, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{away_team} Final Third.png"), 
        dpi = 300)

    plt.clf()



    

    ##########################################################################################
    #          TITLE: HOME HEATMAP
    ##########################################################################################

    df2 = df_base.copy()
    # df2 = df2[(df2['x']!=0) & (df2['y']!=0)]
    df2 = df2.dropna(subset=['playerid']).reset_index(drop=True)

    starterlist = df2.playerid.unique().tolist()
    starterlist = [int(t) for t in starterlist]

    subdf = df2[df2['action']=='SubstitutionOn']
    sublist = subdf.playerid.unique().tolist()
    sublist = [int(t) for t in sublist]
    starterlist = [x for x in starterlist if x not in sublist]

    starterdf = pd.DataFrame({'id':starterlist,'pos':[1]*len(starterlist)})
    subdf = pd.DataFrame({'id':sublist,'pos':[5]*len(sublist)})
    p_dict = pd.concat([starterdf,subdf])

    # ###################################################################################


    df = df_base.copy()
    df["receiver"] = df["playerid"].shift(-1)

    df = df[df['team_name']==home_team]
    events = df[(df['action']=='Pass') & (df['outcome']=='Successful') & (df['ThrowIn']==0)].copy().reset_index(drop=True)
    events_avg = df[(df['action']=='Pass') & (df['ThrowIn']==0)].copy().reset_index(drop=True)
    events = events.dropna(subset=['receiver'])

    p_d = p_dict.copy()
    events['player_name'] = events['playerid']
    events_avg['player_name'] = events_avg['playerid']

    events['receiver_name'] = events['receiver']

    pass_cols = ['player_name', 'receiver']
    passes_formation = events
    location_cols = ['player_name', 'x', 'y']
    location_formation = events

    # average locations
    average_locs_and_count = (events.groupby('player_name')
                              .agg({'x': ['mean'], 'y': ['mean', 'count']}))
    average_locs_and_count.columns = ['x', 'y', 'count']


    average_locs_and_countxxx = (events_avg.groupby('player_name')
                                  .agg({'x': ['mean'], 'y': ['mean', 'count']}))
    average_locs_and_countxxx.columns = ['x', 'y', 'count']


    if average_locs_and_count.index[0] == '':
        average_locs_and_count = average_locs_and_count[1:]

    if average_locs_and_countxxx.index[0] == '':
        average_locs_and_countxxx = average_locs_and_countxxx[1:]


        # calculate the number of passes between each position (using min/ max so we get passes both ways)
    passes_formation['pos_max'] = (events[['player_name',
                                           'receiver_name']]
                                      .max(axis='columns'))
    passes_formation['pos_min'] = (events[['player_name',
                                           'receiver_name']]
                                   .min(axis='columns'))
    passes_formation['id'] = range(1, len(passes_formation) + 1)
    passes_between = passes_formation.groupby(['pos_min', 'pos_max']).id.count().reset_index()
    passes_between.rename({'id': 'pass_count'}, axis='columns', inplace=True)

    # # add on the location of each player so we have the start and end positions of the lines
    passes_between = passes_between.merge(average_locs_and_countxxx, left_on='pos_min', right_index=True)
    passes_between = passes_between.merge(average_locs_and_countxxx, left_on='pos_max', right_index=True,
                                          suffixes=['', '_end'])


    MAX_LINE_WIDTH = 18/2
    MAX_MARKER_SIZE = 3000/2

    passes_between = passes_between[passes_between['pass_count']>=5]

    passes_between['width'] = (passes_between.pass_count / passes_between.pass_count.max() *
                               MAX_LINE_WIDTH)
    average_locs_and_countxxx['marker_size'] = (average_locs_and_countxxx['count']
                                                / average_locs_and_countxxx['count'].max() * MAX_MARKER_SIZE)


    MIN_TRANSPARENCY = 0.3
    color = np.array(to_rgba('black'))
    color = np.tile(color, (len(passes_between), 1))
    c_transparency = passes_between.pass_count / passes_between.pass_count.max()
    c_transparency = (c_transparency * (1 - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
    color[:, 3] = c_transparency

    pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')
    fig, ax = pitch.draw(figsize=(10, 7), constrained_layout=True, tight_layout=False)
    fig.set_facecolor("#F7FFFF")
    pass_lines = pitch.lines(passes_between.x, passes_between.y,
                             passes_between.x_end, passes_between.y_end, lw=passes_between.width,
                             color=color, zorder=1, ax=ax)
    for i in range(len(average_locs_and_countxxx)):
        if p_dict[p_dict['id']==average_locs_and_countxxx.index[i]].pos.values[0] == 5:
            pass_nodes = pitch.scatter(average_locs_and_countxxx.iloc[i].x, average_locs_and_countxxx.iloc[i].y,
                                       s=average_locs_and_countxxx.iloc[i].marker_size,
                                       color='silver', edgecolors='black', linewidth=1, alpha=1, ax=ax)
        else:
            pass_nodes = pitch.scatter(average_locs_and_countxxx.iloc[i].x, average_locs_and_countxxx.iloc[i].y,
                                       s=average_locs_and_countxxx.iloc[i].marker_size,
                                       color=end_color_h, edgecolors='black', linewidth=1, alpha=1, ax=ax)
    for index, row in average_locs_and_countxxx.iterrows():
        path_eff = [path_effects.Stroke(linewidth=1.5, foreground='#4A2E19'), path_effects.Normal()]
        try:
            pitch.annotate(p_d[p_d['id']==row.name].number.values[0], xy=(row.x, row.y),
                           c='white', va='center', path_effects=path_eff,
                           ha='center', size=10, weight='bold', ax=ax)
        except:
            pass



    ax.text(0, 102, "{}\nHeatmap".format(home_team.capitalize()),
            color='#4A2E19',
            va='bottom', 
            ha='left',
            fontdict=title_font)
    ax.text(50,-2, 'Direction of Attack -->',
            color='#4A2E19',
            va='top', 
            ha='center',
            fontdict=label_font)

    fig = plt.gcf()
    fig.set_size_inches(10, 7) #length, height
    
    newax = fig.add_axes([.73, .85, 0.14, 0.14], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{home_team} Heatmap.png"), 
        dpi = 300)

    plt.clf()
    
    
    
    
    
    
    ##########################################################################################
    #          TITLE: Away HEATMAP
    ##########################################################################################
    
    df2 = df_base.copy()
    # df2 = df2[(df2['x']!=0) & (df2['y']!=0)]
    df2 = df2.dropna(subset=['playerid']).reset_index(drop=True)

    starterlist = df2.playerid.unique().tolist()
    starterlist = [int(t) for t in starterlist]

    subdf = df2[df2['action']=='SubstitutionOn']
    sublist = subdf.playerid.unique().tolist()
    sublist = [int(t) for t in sublist]
    starterlist = [x for x in starterlist if x not in sublist]

    starterdf = pd.DataFrame({'id':starterlist,'pos':[1]*len(starterlist)})
    subdf = pd.DataFrame({'id':sublist,'pos':[5]*len(sublist)})
    p_dict = pd.concat([starterdf,subdf])

    # ###################################################################################


    df = df_base.copy()
    df["receiver"] = df["playerid"].shift(-1)

    df = df[df['team_name']==away_team]
    events = df[(df['action']=='Pass') & (df['outcome']=='Successful') & (df['ThrowIn']==0)].copy().reset_index(drop=True)
    events_avg = df[(df['action']=='Pass') & (df['ThrowIn']==0)].copy().reset_index(drop=True)
    events = events.dropna(subset=['receiver'])

    p_d = p_dict.copy()
    events['player_name'] = events['playerid']
    events_avg['player_name'] = events_avg['playerid']

    events['receiver_name'] = events['receiver']

    pass_cols = ['player_name', 'receiver']
    passes_formation = events
    location_cols = ['player_name', 'x', 'y']
    location_formation = events

    # average locations
    average_locs_and_count = (events.groupby('player_name')
                              .agg({'x': ['mean'], 'y': ['mean', 'count']}))
    average_locs_and_count.columns = ['x', 'y', 'count']


    average_locs_and_countxxx = (events_avg.groupby('player_name')
                                  .agg({'x': ['mean'], 'y': ['mean', 'count']}))
    average_locs_and_countxxx.columns = ['x', 'y', 'count']


    if average_locs_and_count.index[0] == '':
        average_locs_and_count = average_locs_and_count[1:]

    if average_locs_and_countxxx.index[0] == '':
        average_locs_and_countxxx = average_locs_and_countxxx[1:]


        # calculate the number of passes between each position (using min/ max so we get passes both ways)
    passes_formation['pos_max'] = (events[['player_name',
                                           'receiver_name']]
                                      .max(axis='columns'))
    passes_formation['pos_min'] = (events[['player_name',
                                           'receiver_name']]
                                   .min(axis='columns'))
    passes_formation['id'] = range(1, len(passes_formation) + 1)
    passes_between = passes_formation.groupby(['pos_min', 'pos_max']).id.count().reset_index()
    passes_between.rename({'id': 'pass_count'}, axis='columns', inplace=True)

    # # add on the location of each player so we have the start and end positions of the lines
    passes_between = passes_between.merge(average_locs_and_countxxx, left_on='pos_min', right_index=True)
    passes_between = passes_between.merge(average_locs_and_countxxx, left_on='pos_max', right_index=True,
                                          suffixes=['', '_end'])


    MAX_LINE_WIDTH = 18/2
    MAX_MARKER_SIZE = 3000/2

    passes_between = passes_between[passes_between['pass_count']>=5]

    passes_between['width'] = (passes_between.pass_count / passes_between.pass_count.max() *
                               MAX_LINE_WIDTH)
    average_locs_and_countxxx['marker_size'] = (average_locs_and_countxxx['count']
                                                / average_locs_and_countxxx['count'].max() * MAX_MARKER_SIZE)


    MIN_TRANSPARENCY = 0.3
    color = np.array(to_rgba('black'))
    color = np.tile(color, (len(passes_between), 1))
    c_transparency = passes_between.pass_count / passes_between.pass_count.max()
    c_transparency = (c_transparency * (1 - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
    color[:, 3] = c_transparency

    pitch = Pitch(pitch_type='opta', pitch_color='#F7FFFF', line_color='#4A2E19')
    fig, ax = pitch.draw(figsize=(10, 7), constrained_layout=True, tight_layout=False)
    fig.set_facecolor("#F7FFFF")
    pass_lines = pitch.lines(passes_between.x, passes_between.y,
                             passes_between.x_end, passes_between.y_end, lw=passes_between.width,
                             color=color, zorder=1, ax=ax)
    for i in range(len(average_locs_and_countxxx)):
        if p_dict[p_dict['id']==average_locs_and_countxxx.index[i]].pos.values[0] == 5:
            pass_nodes = pitch.scatter(average_locs_and_countxxx.iloc[i].x, average_locs_and_countxxx.iloc[i].y,
                                       s=average_locs_and_countxxx.iloc[i].marker_size,
                                       color='silver', edgecolors='black', linewidth=1, alpha=1, ax=ax)
        else:
            pass_nodes = pitch.scatter(average_locs_and_countxxx.iloc[i].x, average_locs_and_countxxx.iloc[i].y,
                                       s=average_locs_and_countxxx.iloc[i].marker_size,
                                       color=end_color_a, edgecolors='black', linewidth=1, alpha=1, ax=ax)
    for index, row in average_locs_and_countxxx.iterrows():
        path_eff = [path_effects.Stroke(linewidth=1.5, foreground='#4A2E19'), path_effects.Normal()]
        try:
            pitch.annotate(p_d[p_d['id']==row.name].number.values[0], xy=(row.x, row.y),
                           c='white', va='center', path_effects=path_eff,
                           ha='center', size=10, weight='bold', ax=ax)
        except:
            pass



    ax.text(0, 102, "{}\nHeatmap".format(away_team.capitalize()),
            color='#4A2E19',
            va='bottom', 
            ha='left',
            fontdict=title_font)
    ax.text(50,-2, 'Direction of Attack -->',
            color='#4A2E19',
            va='top', 
            ha='center',
            fontdict=label_font)

    fig = plt.gcf()
    fig.set_size_inches(10, 7) #length, height
    
    newax = fig.add_axes([.73, .85, 0.14, 0.14], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/{away_team} Heatmap.png"), 
        dpi = 300)

    plt.clf()
    
    
    
    
    
    
    ##########################################################################################
    #                   TITLE: MATCH REPORT PRESSURE
    ##########################################################################################

    ccc = 1.5
                                                                                    # this places a numeric value on each area of the pitch
    fin_val = -2
    def_val = -1.5/ccc
    mid_val = -.5/ccc
    int_val = -1
                                                                                    # this places a numeric value on each action of each action
    passval = 1.5                                                                   # passes are valued as 1.5
    shotval_in_val = 5                                                              # shots in the box: 5
    shot_out_val = 2                                                                # shots out of the box: 2
    
    matplotlib.rcParams['figure.dpi'] = 300

    #####################################################################################################
    df = df_base.copy()

    df_pass = df[(df['action']=='Pass') & (df['outcome']=='Successful')].reset_index(drop=True)
    df_def = df_pass[((df_pass['x']<=33.333) & (df_pass['endx']<=33.333))].reset_index(drop=True)
    df_fin = df_pass[((df_pass['x']>=66.666) & (df_pass['endx']<66.666))].reset_index(drop=True)
    df_int = df[df['action']=='Interception'].reset_index(drop=True)

    mid = df_pass[(df_pass['x'].between(33.333,66.666)) & (df_pass['endx'].between(33.333,66.666))
            ].reset_index(drop=True)

    goals_h = df[(df['action']=='Goal') & (df['team_name']==home_team)].reset_index(drop=True)
    goals_a = df[(df['action']=='Goal') & (df['team_name']==away_team)].reset_index(drop=True)
    red_card_h = df[(df['RedCard']==1) & (df['team_name']==home_team)].reset_index(drop=True)
    red_card_a = df[(df['RedCard']==1) & (df['team_name']==away_team)].reset_index(drop=True)

    df_def['val'] = def_val                                                         # if team_name = away_team then the values become negative 
    for i in range(len(df_def)):
            if df_def['team_name'][i] == away_team:
                df_def['val'][i] = -def_val                                         # when the away team makes a successful pass in the defensive third then the 'val' equals 1 

    df_fin['val'] = fin_val
    for i in range(len(df_fin)):
            if df_fin['team_name'][i] == away_team:
                df_fin['val'][i] = -fin_val                                         # when the away team makes a successful pass in the offensive third then the 'val' equals 2 

    mid['val'] = mid_val
    for i in range(len(mid)):
            if mid['team_name'][i] == away_team:
                mid['val'][i] = -mid_val                                            # when the away team makes a successful pass in the middle third then the 'val' equals 0.333 

    df_int['val'] = int_val
    for i in range(len(df_int)):
            if df_int['team_name'][i] == away_team:
                df_int['val'][i] = -int_val                                         # when the away team makes an interception then the 'val' equals 1 

    def_fin = pd.concat([df_def,mid,df_fin,df_int])
    #####################################################################################################

    df = df_base.copy()

    df3 = df[(df['action']=='Pass') &                                               # only taking actions from the final third of the pitch
                           (df['outcome']=='Successful') &
                           (df['endx']>=100-(100/3)) 
                ].reset_index(drop=True)

    shots = df_base[(df_base['action']=='MissedShots') | (df_base['action']=='ShotOnPost') | (df_base['action']=='SavedShot') | (df_base['action']=='Goal')].reset_index(drop=True)
    goals_h = df[(df['action']=='Goal') & (df['team_name']==home_team)].reset_index(drop=True)
    goals_a = df[(df['action']=='Goal') & (df['team_name']==away_team)].reset_index(drop=True)

    shots_in_box = shots[(shots['x']>=83.1) & (shots['y'].between(21.25,100-21.25))].reset_index(drop=True)
    shots_out_box = shots[~((shots['x']>=83.1) & (shots['y'].between(21.25,100-21.25)))].reset_index(drop=True)

    df3['val'] = passval                                                              # Looking at only passes in the final third of the pitch
    for i in range(len(df3)):
        if df3['team_name'][i] == away_team:
                df3['val'][i] = -passval                                              # when the away team has a successful pass in the final third then the pass value is -1.5

    shots_in_box['val'] = shotval_in_val
    for i in range(len(shots_in_box)):
            if shots_in_box['team_name'][i] == away_team:
                shots_in_box['val'][i] = -shotval_in_val                              # when the away team has a shot in the box then the value is -5

    shots_out_box['val'] = shot_out_val
    for i in range(len(shots_out_box)):
            if shots_out_box['team_name'][i] == away_team:
                shots_out_box['val'][i] = -shot_out_val                               # when the away team has a shot out of the box then the value is -2

        # df3 = df3.append(shots_in_box)
        # df3 = df3.append(shots_out_box)

    df3 = pd.concat([df3,shots_in_box,shots_out_box])

    def_fin = pd.concat([def_fin,df3])

    #####################################################################################################
    df3 = def_fin.reset_index(drop=True).copy()

    bins = np.arange(0,max(df['minute'])+1)
    df3['pressure_bins'] = pd.cut(df3['minute'], bins)
    df3 = df3.dropna(subset=['pressure_bins'])

    A = df3.groupby("pressure_bins", as_index=False)["val"].sum()

    A['3-Minute MA Pressure'] = float(0.0)
    arr = A['val'].values
    i = 0
    # Initialize an empty list to store moving averages
    moving_averages = []

    while i < len(arr):
        period_average = ((1/5)*arr[i]) + ((1/5)*arr[(i-1)]) + ((1/5)*arr[(i-2)]) + ((1/5)*arr[(i-3)]) + ((1/5)*arr[(i-4)])

        moving_averages.append(period_average)
        i += 1

    for j in range(len(moving_averages)):
            A['3-Minute MA Pressure'].iloc[j] = moving_averages[j]
    for q in range(0,(5-1)):
            A['3-Minute MA Pressure'].iloc[q] = np.nan

    A['minute'] = np.arange(0,len(A))

    ax = sns.lineplot(x=A["minute"], y=A["3-Minute MA Pressure"], color='#4A2E19', lw=1)

    for i in range(len(goals_h)):
            ax.axvline(x=goals_h.minute[i], ymin=.5, color=end_color_h, ls='solid', lw=3.5)
            ax.axvline(x=goals_h.minute[i], ymin=.5, color=end_color_h, ls='solid', lw=2.5)
    for i in range(len(goals_a)):
            ax.axvline(x=goals_a.minute[i], ymax=.5, color=end_color_a, ls='solid', lw=3.5)
            ax.axvline(x=goals_a.minute[i], ymax=.5, color=end_color_a, ls='solid', lw=2.5)
    for i in range(len(red_card_h)):
            ax.axvline(x=red_card_h.minute[i], ymin=.5, color='white', ls='-.', lw=2.5)
            ax.axvline(x=red_card_h.minute[i], ymin=.5, color='red', ls='-.', lw=1.5)
    for i in range(len(red_card_a)):
            ax.axvline(x=red_card_a.minute[i], ymax=.5, color='white', ls='-.', lw=2.5)
            ax.axvline(x=red_card_a.minute[i], ymax=.5, color='red', ls='-.', lw=1.5)

    ax.set_xlabel(' ', color='#4A2E19')
    ax.set_ylabel('Control Ratio', color='#4A2E19', fontdict=label_font)
    ax.text(-2, 6, 'Game Control Index', color='#4A2E19', va='bottom', ha='left', fontdict=title_font)

    ymax = max(abs(A['3-Minute MA Pressure'].dropna()).values.tolist())

    plt.ylim(-1*(ymax+(ymax*.05)), ymax+(ymax*.05))

    ax.fill_between(A["minute"], 0, A["3-Minute MA Pressure"],
                       where = A["3-Minute MA Pressure"] >=0,
                       color=end_color_h)
    ax.fill_between(A["minute"], 0, A["3-Minute MA Pressure"],
                       where = A["3-Minute MA Pressure"] <=0,
                       color=end_color_a)

    sns.despine()
    ax.grid(False)

    ax.set_facecolor('#F7FFFF')
    fig = plt.gcf()
    fig.patch.set_facecolor('#F7FFFF')

    plt.axhline(y=0, color='k', ls='--', lw=.5)


    fig = plt.gcf()
    fig.set_size_inches(10,7) #length, height
    
    home_team_label = home_team.capitalize()
    away_team_label = away_team.capitalize()
    
    plt.legend(title="", labels=[home_team_label, away_team_label], 
           handles=[
               plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=end_color_h, markersize=20, label=home_team_label),
               plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=end_color_a, markersize=20, label=away_team_label)
           ], loc='upper center', ncol=2, bbox_to_anchor=(0.5, 1.05), fontsize=14)

    # Add a note below the chart
    ax.text(-4, -6.2, "Note: The Control Ratio takes into account passes, interceptions, shots, goals and red cards. Values for passes and shots are designated based\non where on the pitch a pass occurs (defensive, middle and offensive third) and whether a shot was taken inside or outside of the box.", va='top', ha="left", fontsize=9)

    
    newax = fig.add_axes([.73, .87, 0.13, 0.13], anchor='NE', zorder=1)
    newax.imshow(logo)
    newax.axis('off')

    fig.savefig(
        os.path.join(base_path,
                     f"{league}/{gameweek}/Match Report Pressure.png"), 
        dpi = 300)

    plt.clf()
    
    

griffis_match_report(data, 
                     home_team = 'juventus', 
                     away_team = 'inter', 
                     score = '1 : 0', 
                     league = 'serie_a', 
                     gameweek = 'gameweek 30')