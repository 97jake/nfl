#!/usr/bin/env python
# coding: utf-8



import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from scipy.spatial import KDTree


def get_play_csv():
    play_df = pd.read_csv('plays.csv')
    return play_df

def get_week_csv(week_num):

    week = 'week' + str(week_num) + ".csv"

    return pd.read_csv(week)

def get_game_id(gameId,week_df):
    return week_df[week_df['gameId'] == gameId]


play_df = get_play_csv()


def completions_per_play_type():
    #Initialize dictionaries for completion and incompletion rates
    completions = {}
    incompletions = {}

    #Get the unique plays listed in the plays.csv dataframe
    plays = play_df['offenseFormation'].unique()

    #For each play...
    for play in plays:

        #Create a sub-dataframe for each unique play
        sub_play = play_df[play_df['offenseFormation'] == play]

        #Get the total number of completions and incompletions of each play 
        completions[play] = np.size(sub_play[sub_play['passResult'] == 'C'])
        incompletions[play] = np.size(sub_play[sub_play['passResult'] == 'I'])

    #Do cool matplotlib stuff to create the double bar graph
    x = 2*np.arange(len(plays))
    width = .35

    fig, ax = plt.subplots()
    rects1 = ax.barh(x - width/2, completions.values(), width, label='Completions')
    rects2 = ax.barh(x + width/2, incompletions.values(), width, label='Incompletions')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Play type')
    ax.set_ylabel('Total')
    ax.set_title('Completion Rate by Offensive Formation')
    ax.set_yticks(x)
    ax.set_yticklabels(plays)
    ax.legend()


    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')


    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    plt.show()



def get_line_of_scrimmage():

    game_play_df = play_df[play_df['gameId'] == 2018090600]
    game_week_df = week1_df[week1_df['gameId'] == 2018090600]

    ls = list(game_play_df['yardlineNumber'])
    play_id = list(game_play_df['playId'])

    #Create a dictionary to associate line of scrimmage with playID
    play_ls = {}

    num_plays = len(play_id)


    #Populate dictionary
    for i in range(num_plays):
        play_ls[play_id[i]] = ls[i]
    
    return play_ls



def time_in_pocket():
    
    play_df = get_play_csv()
    week1_df = get_week_csv(1)

    game_id = play_df['gameId'].unique()

    #Create dictionary of games, populated with dictionary of plays
    game_pocket = {}

    for game in game_id:

        #Create dataframes of each individual game
        game_play_df = play_df[play_df['gameId'] == game]
        game_week_df = week1_df[week1_df['gameId'] == game]

        #Get the line of scrimmage and playID of each play of the game
        ls = list(game_play_df['yardlineNumber'])
        play_id = list(game_play_df['playId'])

        #Create a dictionary to associate line of scrimmage with playID
        play_ls = {}

        num_plays = len(play_id)

        #Populate dictionary
        for i in range(num_plays):
            play_ls[play_id[i]] = ls[i]


        #Iterate through each play of week 1
        for play in play_id:

            play_pocket = {}

            #Get line of scrimage for the play
            line_of_scrimmage = play_ls[play]

            #Create dataframe of each individual frame
            sub_play = week1_df[week1_df['playId'] == play]

            #Get just the rows of the football
            football_df = sub_play[sub_play['displayName'] == 'Football']

            #Get the yardline of the football at every frame of the play
            football_yard = list(football_df['x'])
            football_yard = [x-10 for x in football_yard]

            for i in range(len(football_yard)):
                if football_yard[i] > 50:
                    football_yard[i] = 100 - football_yard[i]

            #Creates a list of strings of time of each frame
            play_times = list(football_df['time'])

            time_int = []

            #Creates an int of the time of each frame of each play
            for time in play_times:
                time = time[14:-1]
                time = time.replace(":","")
                time = time.replace(".","")

                time_int.append(int(time))

            #Calculates time in pocket for each play
            for i in range(len(play_times)):
                start_time = time_int[i]
                end_time = time_int[i]

                #Checks which side of the line of scrimmage the ball starts on to look when it crosses 
                if football_yard[0] < line_of_scrimmage:
                    if football_yard[i] >= line_of_scrimmage:
                        end_time = time_int[i]
                        break
                else:
                    if football_yard[i] < line_of_scrimmage:
                        end_time = time_int[i]
                        break

            play_pocket[play] = end_time - start_time

        game_pocket[game] = play_pocket
    


#Attempt to calculate average distance between defense and offensive players per play
def average_distance():
    
    week1_df = get_week_csv(1)
    play_df = get_play_csv()

    radius = 1
    close = 0

    wr_df = week1_df[week1_df['position'] == 'WR']
    rb_df = week1_df[week1_df['position'] == 'RB']
    te_df = week1_df[week1_df['position'] == 'TE']

    ss_df = week1_df[week1_df['position'] == 'SS']
    fs_df = week1_df[week1_df['position'] == 'FS']
    cb_df = week1_df[week1_df['position'] == 'CB']

    games = week1_df['gameId'].unique()

    for game in games:

        game_df = week1_df[week1_df['gameId'] == game]

        plays = game_df['playId'].unique()

        for play in plays:

            sub_df = game_df[game_df['playId'] == play]

            offense = sub_df[['TE','RB','WR']]

            defense = sub_df[['CB','SS','FS']]

            frames = sub_df['frameId'].unique()

            for frame in frames:

                offense_x = offense['x']
                offense_y = offense['y']
                defense_x = defense['x']
                defense_y = defense['y']

                offense_coord = list(zip(offense_x,offense_y))
                defense_coord = list(zip(defense_x,defense_y))

                for i in range(len(offense_coord)):
                    for j in range(len(defense_coord)):
                        distance = (offense_coord[i][0] - defense_coord[j][0])**2 + (offense_coord[i][1] - defense_coord[j][1])**2
                        if distance < radius:
                            count+=1



#The average_distance() function was an attempt to find the average distance between a defender and an offensive player during the course 
# of a play but it didn't work because it proved difficult finding the nearest defender at any given moment.
#So in this function I use a KDTree to find the nearest neighbor of an offensive player to find the closest defender

def kd_tree_distance():

    #Get csv data
    week1_df = get_week_csv(1)
    play_df = get_play_csv()


    frame_average = []
    play_average = {}

    #Get unique games in week 1
    games = list(week1_df['gameId'].unique())

    #Start with first game
    game_df = week1_df[week1_df['gameId'] == games[0]]

    #Get unique plays in first game
    plays = list(game_df['playId'].unique())

    for play in plays:

        #Get play dataframe
        play_df = game_df[game_df['playId'] == play]

        #Get unique frames in play
        frames = list(play_df['frameId'].unique())

        for frame in frames:

            distances = []

            #Get frame dataframe
            frame_df = play_df[play_df['frameId'] == frame]

            #Lists of offensive and defensive players
            offensive_players = ['WR','TE','FB']
            defensive_players = ['SS','FS','CB','LB','MLB']

            #Get dataframes of offensive and defensive players
            o_df = frame_df[frame_df['position'].isin(offensive_players)]
            d_df = frame_df[frame_df['position'].isin(defensive_players)]

            #Coordinates of offensive players
            o_x_coord = list(o_df['x'])
            o_y_coord = list(o_df['y'])

            #Coordinates of defensive players
            d_x_coord = list(d_df['x'])
            d_y_coord = list(d_df['y'])

            o_zipped_coord = list(zip(o_x_coord,o_y_coord))
            d_zipped_coord = list(zip(d_x_coord,d_y_coord))

            #Create KD tree of defensive players
            train_tree = KDTree(d_zipped_coord)

            #Find nearest defensive neighbor
            for player in o_zipped_coord:
                distance, indices = train_tree.query(player, 1)
                distances.append(distance)

            #Find average defensive distance
            frame_average.append(sum(distances)/len(distances))

        play_average[play] = sum(frame_average)/len(frame_average)
        
    return play_average



#The following creates a dictionary connecting a play ID to the targeted player

def intended_target(gameId):
    
    week1_df = get_week_csv(1)
    play_df = get_play_csv()
    
    offensive_players = ['WR','TE','FB','RB','QB']
    
    game_df = week1_df[week1_df['gameId'] == gameId]
    
    plays = list(game_df['playId'].unique())

    
    o_players = {}
    targeted_player = {}
    
    for play in plays:
        
        #Get play dataframe
        sub_df = game_df[game_df['playId'] == play]

        #Get list of frames
        frames = list(sub_df['frameId'].unique())

        #Get frame dataframe
        frame_df = sub_df[sub_df['frameId'] == frames[-1]]
        #print(frame_df)

        #Get offensive players dataframe
        o_df = frame_df[frame_df['position'].isin(offensive_players)]
        #print(o_df)

        #Get dataframe for football
        football_df = frame_df[frame_df['displayName']=='Football']
        #print(football_df)

        #Get NFL ID's and names
        o_id = list(o_df['nflId'])
        o_name = list(o_df['displayName'])

        #Create dictionary mapping ID to name
        for i in range(len(o_id)):
            o_players[o_id[i]] = o_name[i]

        #Get offensive player coordinates
        o_x_coord = list(o_df['x'])
        o_y_coord = list(o_df['y'])

        #Get football coordinates
        football_x_coord = list(football_df['x'])
        football_y_coord = list(football_df['y'])

        #Zip coordinates into tuple
        o_zipped_coord = list(zip(o_x_coord,o_y_coord))
        football_coord = list(zip(football_x_coord,football_y_coord))

        #Create tree of offensive players
        tree = KDTree(o_zipped_coord)

        #Get closest offensive player to ball
        distance,index = tree.query(football_coord[0],1)

        targeted_player[play] = o_name[index]

    return targeted_player
        
        
        
        
targeted_player = intended_target(2018090600)


print(targeted_player[3066])





