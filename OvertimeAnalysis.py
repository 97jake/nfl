#!/usr/bin/env python
# coding: utf-8


from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
from matplotlib import pyplot as plt



def get_abbreviations():
    """

    Returns
    -------
    Prints a list of acceptable team abbreviations

    """
    play_df = pd.read_csv('plays.csv')
    team_abbreviations = list(play_df['possessionTeam'].unique())
    
    new_team_abbr = [team.lower() for team in team_abbreviations]
    
    print("Available teams - ")
    print(new_team_abbr)
    

def get_drive_info(team_abbr,year):
    """
    

    Parameters
    ----------
    team_abbr : str 
        Two or three letter standard NFL team abbreviation. Check get_abbreviations() for more info
    year: int or str
        Year of season that you want to examine. Min year undetermined

    Returns
    -------
    results : list(tuple)
        List of tuples containing info about each drive. Each tuple is formatted as follows - 
            (Team Name (str,abbreviation), Result of Play (str), Starting YardLine (int))

    """
    
    #Get list of ESPN assigned game ids for corresponding season
    game_ids = get_game_ids(team_abbr,year)
    
    results = []
    
    #Loop through each game of the season
    for game in game_ids:
        
        my_url = 'https://www.espn.com/nfl/playbyplay?gameId={}'.format(game)
        
        req = requests.get(my_url)
        my_text = req.text
        soup = bs(my_text, 'html.parser')
        
        #Get the headline result of each drive (ie. 'Touchdown', 'Punt', etc)
        headlines = [item.get_text() for item in soup.find_all('span', class_='headline')]
        
        #Focuses on main table containing all the drives
        sub_soup = soup.find(id='main-container')
        
        #Gets the team acronym at each drive
        logos = sub_soup.find_all('span', class_='home-logo')

        team = re.compile("nfl/500/([a-z]{3})")

        team_abbrs = []

        for stuff in logos:
            team_logo = team.findall(str(stuff))
            
            if team_logo:
                team_logo = team_logo[0]
            else:
                pass

            team_abbrs.append(team_logo)
        
        #Get a list of tuples containing starting yard information
        starting_yard = get_starting_yard(game,team_abbr)
        yards = []
        
        #Process starting yard data to determine starting yard
        #Consists of determining which side of the field team is on to calculate accordingly
        for item in starting_yard:
            myTeam = item[0]
            yard = item[1]
            
            if myTeam == team_abbr:
                yards.append(100 - int(yard))
            else:
                yards.append(int(yard))
        
        #Create tuple of information
        for i in range(len(headlines)):
            detail_tuple = (team_abbrs[i],headlines[i],yards[i])
            results.append(detail_tuple)

    #Return list of tuples
    return results
        

def get_game_ids(team_abbr,year):
    """

    Parameters
    ----------
    team_abbr : str
        Official NFL abbreviation of team
    year : int or str
        Season year

    Returns
    -------
    game_ids : list(str)
        List of strings containing all the ESPN assigned game ids for a given season

    """
    game_ids = []
    
    my_url = 'https://www.espn.com/nfl/team/schedule/_/name/{}/season/{}'.format(team_abbr,year)

    req = requests.get(my_url)
    my_text = req.text
    soup = bs(my_text, 'html.parser')
    
    """
    The majority of this code consists of looking at the main season page and then
    looking at the links to each game. Each link is formatted in a way that contains
    the game id for that specific game, which we extract using Regular Expressions
    and append to a list
    """
    
    sub_soup = soup.find('section',class_='pt0')
    
    links = sub_soup.find_all('a',class_='AnchorLink')
    
    gameID = re.compile("gameId/([0-9]*)")
    
    #Iterate through each link found on page
    for stuff in links:
        
        #Convert the html code to a string
        #Basically at this point I just want to search the string, not the code
        # so it's easier to convert it to a string
        stuff = str(stuff)
        
        game_id = gameID.findall(stuff)
        
        #If I find a game ID, append it to the list
        if game_id:
            game_ids.append(game_id[0])
    
    return game_ids

def get_starting_yard(game_id,team_abbr):
    """

    Parameters
    ----------
    game_id : int or str
        ID of game to look at
    team_abbr : str
        Official NFL team abbreviation. See get_abbreviations() for list of abbreviations

    Returns
    -------
    actions : list(tuple)
        A list of tuples each containing the team side and the yard number per drive

    """    
    
    my_url = 'https://www.espn.com/nfl/playbyplay?gameId={}'.format(game_id)
    
    yard = re.compile("([0-9]{1,2})")
    team = re.compile("([A-Z]{2,3})")

    req = requests.get(my_url)
    my_text = req.text
    soup = bs(my_text, 'html.parser')

    #Get HTML corresponding to the table of drives
    sub_soup = soup.find(id='main-container')
    
    #Get HTML for each individual drive
    action_soup = sub_soup.find_all('ul', class_='drive-list')
    
    actions = []

    #Loop through each drive of the given game
    for stuff in action_soup:
        
        #Find each play from the current drive
        test = stuff.find_all('h3')
        
        #So this bit of code is treating a very strange, specific case where 
        #ESPN makes an error and puts the plays out of order. Basically I say that
        #I want to find the first 'lowest drive', which in theory should always be 
        # a first down, but in reality it's not
        driveDowns = []
        for downs in test:
            downText = downs.get_text()
            if not downText:
                pass
            else:
                driveDowns.append(downText[0])
        driveDowns.sort()
        
        #Accounts for drives with no plays (it's stupid, I know)
        if not driveDowns:
            actions.append((team_abbr,-1))
            continue

        driveSearch = driveDowns[0]
        
        #Iterate through each play of the drive
        for things in test:
            action_text = things.get_text()
            
            #Filter empty data
            if not action_text:
                pass
            
            else:
                #Get the specific down number (first element in current string)
                down = action_text[0]
                
                #Make sure that the down number is the lowest available down
                if down != driveSearch:
                    pass
                else:
                    
                    #Create the drive tuple
                    num = list(yard.findall(action_text))[-1]
                    if num == '50':
                        actions.append((team_abbr,num))
                    else:
                        myTeam = list(team.findall(action_text))[0]
                    
                        drive_info = (myTeam, num)
                    
                        actions.append(drive_info)
    
    return actions



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

print("hello")

