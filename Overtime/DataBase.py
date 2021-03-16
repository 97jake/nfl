# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 08:49:46 2021

@author: 97jak
"""

import sqlite3 as sql
import OvertimeAnalysis as oa

years = [2010+i for i in range(11)]
teams = oa.get_abbreviations()

def create_data_base():
    with sql.connect('overtime.db') as conn:
        cur = conn.cursor()
        try:
            cur.execute("DROP TABLE DriveInfo;")
        except:
            pass
        
        try:
            cur.execute("CREATE TABLE DriveInfo (Year INTEGER, Team TEXT, GameID TEXT, Opponent TEXT, Yardline INTEGER, Result TEXT)")
        except:
            print("Error creating table")
            
    conn.close()
    
conn = sql.connect('overtime.db')

def populate_database(team_abbr,year):
    
    cur = conn.cursor()

    team_rows = oa.get_drive_info(team_abbr,year)
    
    for item in team_rows:
        if type(item[4]) != type(2):
            team_rows.remove(item)
            print("Removed item: {} because of {}".format(item,item[4]))
        
        if type(item[0]) != type(2):
            team_rows.remove(item)
            print("Removed item: {} because of {}".format(item,item[0]))
            
        if type(item[1]) != type("h"):
            team_rows.remove(item)
            print("Removed item: {} because of {}".format(item,item[1]))
        if type(item[2]) != type('h'): 
            team_rows.remove(item)
            print("Removed item: {} because of {}".format(item,item[2]))
        if type(item[3]) != type('h'):
            team_rows.remove(item)
            print("Removed item: {} because of {}".format(item,item[3]))
            print("Removed item because {} is type {} and not type {}".format(item[3],type(item[3]),type('h')))
        if type(item[5]) != type('h'):
            team_rows.remove(item)
            print("Removed item: {} because of {}".format(item,item[5]))

    
    try:
        cur.executemany("INSERT INTO DriveInfo VALUES(?,?,?,?,?,?);", team_rows)
    except:
        print("Error adding rows for {} in {}".format(team_abbr,year))
        
    conn.commit()

teams = ['atl', 'phi', 'pit', 'cle', 'cin', 'ind', 'ten', 'mia', 'bal', 'buf', 'ne', 'hou', 'jax', 'nyg', 'no', 'tb', 'was', 'ari', 'car', 'dal', 'gb', 'chi', 'nyj', 'det', 'oak', 'la', 'min', 'lac', 'kc', 'sf', 'den', 'sea']
create_data_base()


team = 'bal'
for year in years:
    print("Populating database: Team={},Year={}".format(team,year))
    populate_database(team,year)
    print("Successfully populated database: Team={},Year={}".format(team,year))
        
print("Successfully made it to the end!!!")

conn.close()