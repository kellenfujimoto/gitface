#!/usr/bin/python
# -*- coding: utf-8 -*-
import gitface

# Classes
# Attempt to remake menu as class

publicKey = raw_input("Do you have an RSA public key? If so, paste it here. If not, hit return and one will be generated for you. ")
timeline = gitface.Stream(pubKey = publicKey)

class Menu(object):

    """Gitface main menu"""

    def __init__(self):
        self.nav = ''
        self.items = []
        self.description = ''


# Functions

def menu():

    print '''Create (n)ew post?
Show public (t)imeline?
(q)uit application?
Manage (r)ings?'''
    nav = raw_input()
    if nav == "r":
        print "Sorry, rings aren't implemented yet! Please select a different option."
        menu()
    elif nav == "b":
        stream = gitface.Stream()
        print "Success!\n"
        menu()
    elif nav == "n":
    	newPost = gitface.Entry()
        author = raw_input('Author? ')
        category = raw_input('Category? ')
        if category == '':
            category = 'uncategorized'
        body = raw_input('What do you want to say?\n')
        content = ["author", author, "category", category, "body", body]
        newPost.post(content)
        menu()
    elif nav == 't':

        for row in timeline.command('select * from stream order by timestamp desc limit 10;'):
            print row[4], '<|> By', row[1], 'in', row[2], '''
---
''', \
                row[3], '\n'
        menu()
    elif nav == 'q':
        print 'Bye!'
    else:
        print 'Please try again\n'
        menu()


        # end main menu function

def touch(file):
    f = open(file, 'w+', 0)
    f.close()


def selectRing():
    keyDB = sqlite3.connect('keys.db')
    keyDBc = keyDB.cursor()
    keyDBc.execute('select * from keys')
    keyDB.commit()
    count = 1
    for row in keyDBc:
        print '(' + str(count) + ') Ring', row[0], ' | ', row[2]
        count += 1
    currentRing = raw_input()
    if int(currentRing) >= count:
        print 'Please select a ring listed above.\n'
        selectRing()
    print 'Success!'


##################################################
# Begin Program

touch('~/gitface/gitface.db')

print 'Rings:\n'
timeline.printRings()
currentRing = -1
while not -1 < currentRing < timeline.command("select count(*) from keys"):
	currentRing = raw_input("Which ring do you choose?\n")
main = Menu()
main.__setattr__(self, description,
                 'Welcome to the main menu of CommFace, a GitFace client.'
                 )
