#!/usr/bin/env python
# coding: utf-8


from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd




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



team_list[:20]





