#!/usr/bin/python
# -*- coding: utf-8 -*-

# Gitface

import os
from Crypto.PublicKey import RSA
from Crypto.Random import random
from Crypto.Hash import SHA512
import scrypt
import getpass
import re

# sqlalchemy imports
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

# Password security functions

def randString(length):
	return ''.join(chr(random.randrange(0, 255)) for i in range(length))


def verifyPassword(hashedPassword, guessedPassword, maxtime=0.1):
	try:
		scrypt.decrypt(hashedPassword, guessedPassword, maxtime)
		return True
	except scrypt.error:
		return False

# Other functions

def touch(file):
	if os.path.exists(os.path.dirname(file)) == False:
		os.makedirs(os.path.dirname(file))
	f = open(file, 'w+', 0)
	f.close()

# Constants
# Might toss all of these into a configuration file. Once it gets too verbose.
# dbPass = getpass.getpass()

gitfaceDir = "/" + os.path.abspath(os.path.expanduser(os.path.normcase('~/gitface')))  # Protect the Windows users' paths

# osPassword = getpass.getpass("Password for " + getpass.getuser() + ": ")


# sqlalchemy
engine = create_engine("postgresql+psycopg2://gitface:faster@localhost/gitface")
# engine.raw_connection().connection.text_factory = str

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'

	id = Column(String, primary_key=True)
	username = Column(String, nullable=False, unique=True)
	passhash = Column(LargeBinary)
	personalKey = Column(String)
	sharingKey = Column(String)
	posts = relationship('Entry', backref='users')

	def __init__(self, username, password, keypassphrase, personalKey, sharingKey):
		self.username = username
		id = SHA512.new(self.username)
		self.id = id.digest()
		passhash = SHA512.new(password + id.digest())
		self.passhash = passhash.digest()
		if personalKey == "new":
			rawRSA = RSA.generate(2048)
			self.personalKey = rawRSA.exportKey(passphrase=keypassphrase)
		else:
			self.personalKey = RSA.importKey(passphrase=keypassphrase)
		if sharingKey == "new":
			rawRSA = RSA.generate(2048)
			self.sharingKey = rawRSA.exportKey(passphrase=keypassphrase)
		else:
			self.sharingKey = RSA.importKey(passphrase=keypassphrase)

	def __repr__(self):
		return "<User('%s','%s','%s','%s')>" % (self.username, self.passhash, self.personalKey.digest(), self.sharingKey.digest())

class Ring(Base):
	__tablename__ = 'rings'

	id = Column(Integer)
	ring = Column(Integer, primary_key=True)
	key = Column(String)

	def __init__(self, ring, key, keypassphrase):
		self.ring = ring
		if key == "new":
			rawRSA = RSA.generate(2048)
			self.key = rawRSA.exportKey(passphrase=keypassphrase)
		else:
			self.key = RSA.importKey(passphrase=keypassphrase)

	def __repr__(self):
		return "<Ring('%s', '%s')>" % (self.ring, self.key.digest())


class Entry(Base):
	__tablename__ = 'stream'

	id = Column(Integer, primary_key=True)
	ring = Column(Integer, ForeignKey('rings.ring'))
	user_id = Column(String, ForeignKey('users.id'))
	author = Column(String)
	data = Column(String)

	def __init__(self, author, ring, data):
		self.ring = ring
		foo = SHA512.new(data=author)
		self.user_id = foo.digest()
		self.author = author
		self.data = data

	def __repr__(self):
		return "<Entry('%s','%s')>" % (self.ring, self.data)

Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

class Menu(object):

    """Gitface main menu"""

    def __init__(self, items, description):
        self.items = items
        self.description = description

def passwordConfirmation(query = 'password:'):
	guess1 = getpass.getpass(query)
	guess2 = getpass.getpass("Confirm " + query)
	if guess1 == guess2:
		return guess1
	else:
		print "Password error. Please try again.\n"
		passwordConfirmation()

def userVerify():
	selectedUser = raw_input("Username? ")
	if selectedUser == "guest":
		return selectedUser
	userList = []
	for row in session.query(User.username).filter(User.username == selectedUser):
		userList.append(row)
	if len(userList) == 0:
		action = raw_input("Username not found. Would you like to create a new user called " + selectedUser + "?(y/n) ")
		if action == "y":
			newpassHash = SHA512.new(passwordConfirmation())
			newpassphrase = passwordConfirmation("private passphrase: ")
			newUser = User(selectedUser, newpassHash.digest(), newpassphrase, "new", "new")
			userHash = SHA512.new(selectedUser)
			session.add(newUser)
			session.commit()
		else:
			userVerify()
	else:
		return selectedUser

#################
# Begin program #
#################

touch('~/gitface/gitface.db')
activeUser = userVerify()

hashedPassword = ""

for row in session.query(User.passhash).filter(User.username == activeUser):
	hashedPassword = row[0]
# hashedPassword = session.query(User.passhash).filter_by(username=activeUser)
guessHash = SHA512.new(getpass.getpass("Password? "))
passwordGuess = guessHash.digest()


while not hashedPassword == passwordGuess:
	print hashedPassword, passwordGuess
	passwordGuess = getpass.getpass("Hm, something went wrong. Try again? ")

print "Successfully logged in as " + activeUser + ".\n"

main = Menu(items=["Create (n)ew post?", "Show public (t)imeline?", "(q)uit application?"], description="Welcome to the main menu of GitFace! Please select a navigation option below:\n")

nav = ''

while nav != 'q':
	print main.description
	for x in main.items:
		print x
	nav = raw_input('What would you like to do? ')
	if nav == 'n':
		if activeUser == 'guest':
			print 'Warning: the only option for guests is the unencrypted public ring.\n'
			body = raw_input("What would you like to say? \n")
			entry = Entry(0, "guest", body)
			session.add(entry)
		else:
			activeUserHash = SHA512.new(activeUser)
			for ring in session.query(Entry).filter(username = activeUserHash.digest()):
				print ring
			currentRing = raw_input("\nChoose a ring#: ")
			ringKey = session.query(Ring.key).filter(ring = currentRing)
			rawBody = raw_input("What would you like to say?\n")
			body = ringKey.encrypt(rawBody)
			entry = Entry(currentRing, activeUser, body)
			session.add(entry)
	elif nav == 't':
		count = 1
		for entry in session.query(Entry).order_by(Entry.id):
			print str(count) + str(entry.ring) + " | by guest\n" + entry.data + "\n---\n"
			count += 1
		entrySelect = raw_input("Press return to go to the main menu.")
		# if not entrySelect:
# 			pass
# 		else:
# 			print session.query(Entry).order_by(Entry.id)[int(entrySelect) + 1]
# 			entryAction = raw_input("
			# need to support decrypting

	session.commit()