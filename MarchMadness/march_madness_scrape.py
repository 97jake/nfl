# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 08:34:36 2021

@author: 97jak
"""

from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import sqlite3 as sql

def get_dropdown_options():
    my_url = 'https://www.ncaa.com/stats/basketball-men/d1'
    
    req = requests.get(my_url)
    my_text = req.text
    soup = bs(my_text, 'html.parser')
    
    
    subsoup = soup.find_all('div',class_ = 'stats-header__filter')[1]
    
    my_options = subsoup.find_all('option')
    
    options = [item.get_text() for item in my_options][1:]
    
    with open('options.txt','w') as file:
        for i in range(len(options)):
            file.write(options[i]+'\n')

def get_teams():
    
    pages = ['/p{}'.format(i) if i>1 else '' for i in range(1,7)]
    
    my_url = 'https://www.ncaa.com/stats/basketball-men/d1/current/team/625'
    teams = set()
    
    for j in range(len(pages)):
        new_url = my_url+pages[j]
    
        req = requests.get(new_url)
        my_text = req.text
        soup = bs(my_text, 'html.parser')
        
        table = soup.find_all('table')[0]
        #schools = table.find_all('a')
        #school_list = [school.get_text() for school in schools]
        
        stuff = table.find_all('td')
        my_stuff = [things.get_text() for things in stuff]
        
        #ranks = [my_stuff[5*i] for i in range(50)]
        teams_list = [my_stuff[5*i+1] for i in range(50)]
        for team in teams_list:
            teams.add(team)
        
    return teams

def get_urls():
    
    my_url = 'https://www.ncaa.com/stats/basketball-men/d1'
    
    req = requests.get(my_url)
    my_text = req.text
    soup = bs(my_text, 'html.parser')
    
    
    subsoup = soup.find_all('div',class_ = 'stats-header__filter')[1]
    my_options = subsoup.find_all('option')[1:]
    
    ids = re.compile("team/([0-9]*)")
    
    url_ids = [ids.findall(str(thing)) for thing in my_options]
    options = [thing.get_text() for thing in my_options]
    
    url_ids = [stuff[0] for stuff in url_ids]
    
    return {options[i]:url_ids[i] for i in range(len(url_ids))}

def get_stats():
    my_url = 'https://www.ncaa.com/stats/basketball-men/d1/current/team/'
    pages = ['/p{}'.format(i) if i>1 else '' for i in range(1,8)]
    
    url_dict = get_urls()
    url_ids = list(url_dict.values())
    stats = list(url_dict.keys())
    
    team_set = get_teams()
    team_list = list(team_set)
    team_dict = {}
    #print(team_list)
    
    for team in team_list:
        team_dict[team] = {}
    
    for j,_id in enumerate(url_ids):
        
        for page in pages:
            
            new_url = my_url+_id+page
            #print(new_url)
            req = requests.get(new_url)
            my_text = req.text
            soup = bs(my_text, 'html.parser')
            
            table = soup.find_all('table')[0]
            #schools = table.find_all('a')
            #school_list = [school.get_text() for school in schools]
            
            stuff = table.find_all('tr')[1:]
            if stuff:
                for row in stuff:
                    if row:
                        #print(row)
                        nums = row.find_all('td')
                        if nums:
                            nums = [cosas.get_text() for cosas in nums]
                            #print(nums)
                            team_check = nums[1]
                            if team_check in team_set:
                                team_dict[team_check][stats[j]] = nums[-1]
                            else:
                                team_set.add(team_check)
                                team_dict[team_check] = {}
                                team_dict[team_check][stats[j]] = nums[-1]
                                #print("{} is not in team set".format(team_check))
    
    
    return team_dict


def create_database():
    with sql.connect('ncaa.db') as conn:
        cur = conn.cursor()
        try:
            cur.execute("DROP TABLE TeamStats;")
        except:
            pass
        
        
        cur.execute("CREATE TABLE TeamStats (Team TEXT, FieldGoalAttempts REAL, AssistTurnoverRatio REAL, AssistsPerGame REAL, BlocksPerGame REAL, DefReboundsPerGame REAL, Fouls REAL, Turnovers REAL, FieldGoalPct REAL, FieldGoalPctDefense REAL, FreeThrowAttemps REAL, FreeThrowsMade REAL, FreeThrowPct REAL, OffReboundsPerGame REAL, PersonalFoulsPerGame REAL, ReboundMargin REAL, ScoringDefense REAL, ScoringMargin REAL, ScoringOffense REAL, StealsPerGame REAL, ThreePtFieldGoalDefense REAL, ThreePtPerGame REAL, ThreePtPct REAL, ThreePtTotal REAL, AssistsTotal REAL, BlocksTotal REAL, ReboundsTotal REAL, ReboundsPerGame REAL, StealsTotal REAL, TurnoverMargin REAL, TurnoversForced REAL, TurnoversPerGame REAL, WinLosePct REAL)")
        
            
    conn.close()
    

def populate_database():
    stats_dict = get_stats()
    
    options_dict = get_urls()
    options = list(options_dict.keys())
    
    teams = list(stats_dict.keys())
    
    with sql.connect('ncaa.db') as conn:
        cur = conn.cursor()
    
        for team in teams:
            team_list = [team]
            sub_dict = stats_dict[team]
            for option in options:
                if option not in sub_dict:
                    team_list.append(10000.)
                else:
                    num = float(sub_dict[option])
                    team_list.append(num)
                    
            row = tuple(team_list)
            #print(row)
            cur.execute("INSERT INTO TeamStats VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);", row)
    
    conn.close()

create_database()
populate_database()
        

