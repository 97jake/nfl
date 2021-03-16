# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 21:41:16 2021

@author: 97jak
"""

import sqlite3 as sql

#This file showcases a couple examples of how you might want to query the database

#Note - see DataBase.py to see how the database is set up, including names of columns
#as well as table name.
#In this database, we use one table called DriveInfo, which contains all of our columns

#Let's say we want to get the Yardline column in a list.
#Begin by opening up a connection to the database
with sql.connect('overtime.db') as conn:
    
    cur = conn.cursor()
    
    #Using our cursor, we select the Yardline column
    cur.execute("SELECT Yardline FROM DriveInfo")
    
    #The fetchall() command gets all the values that match our previously executed command
    #Note - other relevant commands include fetchone() and fetchmany(n)
    yards = cur.fetchall()

#Close database
conn.close()

#A WORD OF CAUTION
#Any fetch command will return a list of tuples, no matter how many columns you select
#Notice that the above command got each yardline as a tuple of the form (80,).
#To fix that, we take the first and only element out of each tuple
yards = [yard[0] for yard in yards]

print("List of yardlines - ")
print(yards[:10])

#Success! Now let's say we want to extract each yardline number with the result of the drive.
#With just a few modifications...
with sql.connect('overtime.db') as conn:
    
    cur = conn.cursor()

    cur.execute("SELECT Yardline,Result FROM DriveInfo")

    info = cur.fetchall()

#Close database
conn.close()

print("\nList of (yardline,result) tuples - ")
print(info[:10])

#You see that you can add as many column names as you want to get more info in each tuple

#Okay, so we've seen how to get specific column data.
#What if you've had enough and you just want to get all the data. Easy!
with sql.connect('overtime.db') as conn:
    
    cur = conn.cursor()

    cur.execute("SELECT * FROM DriveInfo")

    info = cur.fetchall()

#Close database
conn.close()

print("\nList containing everything - ")
print(info[:10])

#So we see that the * acts as an "all" command, getting everything in a table. 

#Okay, but that's the easy stuff. Let's bump it up a notch. 
#The ultimate goal here is to bin the data by yards right?
#Let's add some parameters to the yardline column

with sql.connect('overtime.db') as conn:
    
    cur = conn.cursor()

    cur.execute("SELECT DI.Yardline " "FROM DriveInfo AS DI " "WHERE DI.Yardline >= 10 AND DI.Yardline<20")

    info = cur.fetchall()

#Close database
conn.close()

info = [stuff[0] for stuff in info]
print("\nList of starting yardlines between 10 and 20")
print(info)

#Okay, so there's a couple of things here
#One - THE SPACE BETWEEN THE FIRST TWO COMMANDS AND THEIR CLOSING QUOTATION MARKS
#IS ABSOLUTELY NECESSARY
#Two - You can add multiple constraints to any column you want using the AND command
#Three - There are no commas between each section. These are all commands, not 
#parameters of execute()

#Finally, since I want an average, maybe I want to get the number of drives
#matching a certain condition. 
#We can use functions to help us here

with sql.connect('overtime.db') as conn:
    
    cur = conn.cursor()

    cur.execute("SELECT COUNT(DI.Yardline) " "FROM DriveInfo AS DI " "WHERE DI.Yardline >= 10 AND DI.Yardline<20")

    info = cur.fetchall()

#Close database
conn.close()

print("\nNumber of drives starting at a yardline between 10 and 20 - ")
print(info[0][0])

#Note the double index of info here.
#This is because we still get a list of tuples, both of which contain one element

#Hope this helps!

