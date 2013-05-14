import datetime
import os
from os import path
import sqlite3
 
# Constants
gitDir = path.expanduser(path.normpath("~/gitface"))
 
# Classes
# Attempt to remake menu as class
 
 
# Functions
def menu():
    if path.exists(gitDir + "/comm.db") == False:
        print "Start a new (b)blog?\n"
    print "Create (n)ew post?\nShow public (t)imeline?\n(q)uit application?\nManage (r)ings?"
    nav = raw_input()
    if nav == "r":
    	print "Sorry, rings aren't implemented yet! Please select a different option."
    	menu()
    elif nav == "b":
        conn = sqlite3.connect(gitDir + "/comm.db")
        c = conn.cursor()
        c.execute("create table stream (ring integer, author text, category text, body text, timestamp real);")
        conn.commit()
        c.close()
        print "Success! Created blog at ", gitDir
        menu()
    elif nav == "n":
        author = raw_input("Author? ")
        category = raw_input("Category? ")
        if category == "":
            category = "uncategorized"
        body = raw_input("What do you want to say?\n")
        conn = sqlite3.connect(gitDir + "/comm.db")
        c = conn.cursor()
        data = (author, category, body)
        c.execute("insert into stream values (0, ?, ?, ?, datetime('now'));", data)
        conn.commit()
        c.close()
        menu()
    elif nav == "t":
        conn = sqlite3.connect(gitDir + "/comm.db")
        c = conn.cursor()
        c.execute("select * from stream order by timestamp desc limit 10;")
        for row in c:
        print row[4], "<|> By", row[1], "in", row[2],"\n---\n", row[3], "\n"
        menu()
    elif nav == "q":
		print "Bye!"
    else:
		print "Please try again\n"
		menu()
	# end main menu function
 
# ring submenu function
	
 
def touch(directory, file):
	import os
	from os import path
 
	directory = path.normcase(directory)
	directory = path.expanduser(directory)
 
	while not path.exists(directory):
		os.makedirs(directory)
	os.chdir(directory)
	while path.exists(file) == False:
		f = open(file, 'w+', 0)
		f.close()
 
def selectRing():
    keyDB = sqlite3.connect(gitDir + "/keys.db")
    keyDBc = keyDB.cursor()
    keyDBc.execute("select * from keys")
    keyDB.commit()
    count = 1
    for row in keyDBc:
		print "(" + str(count) + ") Ring", row[0], " | ", row[2]
		count += 1
    currentRing = raw_input()
    if int(currentRing) >= count:
        print "Please select a ring listed above.\n"
        selectRing()
    print "Success!"
 
##################################################
# Begin Program
touch(gitDir, "comm.db")
# check if keys.db exists, if not then create it
if path.exists(gitDir + "/keys.db") == False:
	touch(gitDir, "keys.db")
	conn = sqlite3.connect(gitDir + "/keys.db")
	c = conn.cursor()
	c.execute("create table keys (ring integer, pub text, description text);")
	c.execute("insert into keys values (0, '', 'Public, unencrypted posts');")
	conn.commit()
	c.close()
 
print "Which ring do you choose?\n"
selectRing()
menu()