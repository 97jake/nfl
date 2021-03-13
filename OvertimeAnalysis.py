#!/usr/bin/env python
# coding: utf-8


from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
from matplotlib import pyplot as plt




play_df = pd.read_csv('plays.csv')
team_abbreviations = list(play_df['possessionTeam'].unique())

new_team_abbr = [team.lower() for team in team_abbreviations]

print("Available teams - ")
print(new_team_abbr)


def get_drive_info(game_ids):
    """
    

    Parameters
    ----------
    game_ids : list(int)
        List of game ids generated from the get_game_ids() function

    Returns
    -------
    results : list(tuple)
        List of tuples containing info about each drive. Each tuple is formatted as follows - 
            (Team Name (str,abbreviation), Result of Play (str), Starting YardLine)

    """
    
    results = []
    
    for game in game_ids:
        
        my_url = 'https://www.espn.com/nfl/playbyplay?gameId={}'.format(game)

        req = requests.get(my_url)
        my_text = req.text
        soup = bs(my_text, 'html.parser')

        headlines = [item.get_text() for item in soup.find_all('span', class_='headline')]

        sub_soup = soup.find(id='main-container')
        logos = sub_soup.find_all('span', class_='home-logo')

        team = re.compile("nfl/500/([a-z]{3})")

        team_abbr = []

        for stuff in logos:
            team_logo = team.findall(str(stuff))
            
            if team_logo:
                team_logo = team_logo[0]
            else:
                pass

            team_abbr.append(team_logo)

        detail_soup = sub_soup.find_all('span',class_='drive-details')

        yard_pattern = re.compile("(-?[0-9]*) yards?")
        yards = []
        for detail in detail_soup:
            deets = detail.get_text()
            yards.append(yard_pattern.findall(deets)[0])

        for i in range(len(headlines)):
            detail_tuple = (team_abbr[i],headlines[i],yards[i])
            results.append(detail_tuple)

            
    return results
        

def get_game_ids(team_abbr,year):
    game_ids = []
    
    my_url = 'https://www.espn.com/nfl/team/schedule/_/name/{}/season/{}'.format(team_abbr,year)

    req = requests.get(my_url)
    my_text = req.text
    soup = bs(my_text, 'html.parser')
    
    sub_soup = soup.find('section',class_='pt0')
    
    links = sub_soup.find_all('a',class_='AnchorLink')
    
    gameID = re.compile("gameId/([0-9]*)")
    
    for stuff in links:
        stuff = str(stuff)
        
        game_id = gameID.findall(stuff)
        
        if game_id:
            game_ids.append(game_id[0])
    
    return game_ids

def get_starting_yard(game_ids):
        
    my_url = 'https://www.espn.com/nfl/playbyplay?gameId={}'.format(game_ids)

    req = requests.get(my_url)
    my_text = req.text
    soup = bs(my_text, 'html.parser')

    sub_soup = soup.find(id='main-container')
    
    action_soup = sub_soup.find_all('ul', class_='drive-list')
    
    actions = []
    i = 1
    for stuff in action_soup:
        test = stuff.find_all('h3')
        #print("Drive number - {}".format(i))
        for things in test:
            action_text = things.get_text()
            if not action_text:
                pass
            else:
                down = action_text[0]
                if down != "1":
                    pass
                else:
                    #print("Starting position - {}".format(action_text))
                    actions.append(action_text)
                    i+=1
                    break


ids= get_game_ids('bal',2016)



team_list = get_drive_info(ids)



<<<<<<< Updated upstream
team_list[:20]

print("hello world")
=======
#team_list[:20]


def touchdown(team_list, team):
    """
    Function to compile the number of touchdown
    drives in a season with their corresponding lengths.
    
        Parameters 
        --------
        team_list (list) - the list of tuples generated
        by the web scraper corresponding to the teams, the outcome
        of the drive, and the length of the drive
        
        team (str) - a three letter string corresponding to which team's 
        drive info you want to store
    
        Returns
        --------
        lengths (list) - A list of lengths of drives that resulted in touchdowns.
        The length of the drive will be the starting field position for that 
        given drive.
        
        totals (list) - Every starting field position for every drive in the
        given season. Will be used to calculate probability of scoring from
        any given starting field position
    """
    lengths = []
    totals = []
    for item in team_list:
        if item[0] == team:
            totals.append(int(item[2]))
            if item[1] == "Touchdown":
                lengths.append(int(item[2]))
    return lengths, totals


def create_histogram(team_list, team):
    """
    Function that creates a histogram of the
    lengths of touchdown drives for a given team.
    
        Parameters
        ---------
        team (str): three letter string indicator for 
        which team's data will be used.
        
        team_list (list of tuples): List of all tuples
        corresponding to drives from every game, their
        outcome, and the length of the drive
        
        Returns
        --------
        Displays a histogram of the distribution
        of starting field positions on touchdwon drives.
    """
    drive_lengths = touchdown(team_list, team)[0]
    total_drives = touchdown(team_list, team)[1]
    plt.subplot(211)
    plt.hist(total_drives, 20)
    plt.title("All drives")
    plt.tight_layout()
    plt.subplot(212)
    plt.hist(drive_lengths, 20)
    plt.title("Touchdowns")
    plt.tight_layout()
    plt.show()

create_histogram(team_list, 'bal')
>>>>>>> Stashed changes



