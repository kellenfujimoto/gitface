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
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

# Password security functions

def randString(length):
	return ''.join(chr(random.randrange(0, 255)) for i in range(length))


def hashPassword(password, maxTime=0.1, dataLength=64):
	return scrypt.encrypt(randString(dataLength), password,
						  maxtime=maxTime)


def verifyPassword(hashedPassword, guessedPassword, maxTime=0.1):
	try:
		scrypt.decrypt(hashedPassword, guessedPassword, maxTime)
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

gitfaceDir = "/" + os.path.abspath(os.path.expanduser(os.path.normcase('~/gitface')))  # Protect the Windows users' paths

osPassword = getpass.getpass("Password for " + getpass.getuser() + ": ")


# sqlalchemy
engine = create_engine("postgresql+psycopg2://" + os.getlogin() + ":" + osPassword + "@localhost:5432")

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'

	id = Column(String, primary_key=True)
	username = Column(String)
	passhash = Column(String)
	personalKey = Column(String)
	sharingKey = Column(String)

	def __init__(self, username, password, personalKey, sharingKey):
		self.username = username
		id = SHA512(self.username)
		self.id = id.hexdigest()
		self.passhash = hashPassword(password)
		self.personalKey = [RSA.publickey(RSA.importKey(personalKey)), scrypt.encrypt(RSA.importKey(personalKey), password, maxtime=0.1)]
		self.sharingKey = RSA.publickey(RSA.importKey(sharingKey))

	def __repr__(self):
		return "<User('%s','%s','%s','%s')>" % (self.username, self.passhash, personalKey[0], sharingKey[0])

class Entry(Base):
	__tablename__ = 'stream'

	id = Column(Integer, primary_key=True)
	ring = Column(Integer)
# 	user_id = Column(String, ForeignKey('users.id'))
# 	author = relationship(User, primaryjoin=user_id == User.id)
	data = Column(String)

	def __init__(self, ring, data):
		self.ring = ring
# 		foo = SHA512.new(data=author)
# 		self.user_id = foo.digest()
# 		self.author = author
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

# Begin program
touch('~/gitface/gitface.db')
activeUser = 'guest'
main = Menu(items=["Create (n)ew post?", "Show public (t)imeline?", "(q)uit application?"], description="Welcome to the main menu of GitFace! Please select a navigation option below:\n")
# main.__dict__[items] = ("Create (n)ew post?", "Show public (t)imeline?", "(q)uit application?")
# main.__dict__[description] = "Welcome to the main menu of GitFace! Please select a navigation option below:\n"

nav = ''

while nav != 'q':
	print main.description
	for x in main.items:
		print x
	nav = raw_input('What would you like to do? ')
	if nav == 'n':
		if activeUser == 'guest':
			print 'Warning: the only option for guest users is the unencrypted public ring.\n'
			body = raw_input("What would you like to say? \n")
			entry = Entry(0, body)
			session.add(entry)
		else:
			pass # add checking against user, and inserting that into entry object
	elif nav == 't':
		for entry in session.query(Entry).order_by(Entry.id):
			print str(entry.ring) + " | by " + entry.author + "\n---\n" + entry.data
			# need to support decrypting


# Preserved for posterity:

"""class User(object):

	def __init__(self, username='', path=gitfaceDir, password=''):
		if os.path.exists(path) == False:
			os.makedirs(path)
		self.location = path + 'users.db'
		try:
			conn = sqlite3.connect(self.location)
			c = conn.cursor()
			c.execute('create table users (username text, salt text, passhash text, share text);')
		finally:
			pass
		if username == '':
			self.username = raw_input('What is your email address? ')
		checkData = dbExec(self.location,
						   'select salt, passhash from users where username='
							+ self.username + ';')
		if checkData[0] != None:
			self.salt = checkData[0]
		else:
			self.salt = SHA512(data=self.username)
		if checkData[2] != None:
			self.passhash = checkData[2]
		else:
			self.passhash = hashPassword(password,maxtime=0.1)
		if checkData[3] != None:
			self.sharePub = RSA.importKey(checkData[3])
		else:
			x = RSA.generate(2048)
			self.sharePub = x.publicKey()
			self.sharePri = scrypt.encrypt(x.export(),password,maxtime=0.1)
		dbExec(self.location, 'insert into users values (?,?,?,?);' (self.username, self.salt.hexdigest, self.passhash, self.sharePub))"""


"""class Stream(object):

	def __init__(
		self,
		path=gitfaceDir,
		gitfaceDB='gitface.db',
		user='guest',
		):

		self.path = path
		self.gitfaceDB = path + gitfaceDB
		if user != 'guest':
			self.user = User(username=user)

		# Check if gitface database and tables are there; create if not

		if os.path.exists(self.path) == False:
			os.makedirs(self.path)
		f = open(self.path + self.gitfaceDB, 'w+', 0)
		f.close()
		dbExec(self.path + self.gitfaceDB,
			   ['create table if not exists stream (ring integer, index integer,data text, timestamp real);', 'create table if not exists keys (ring text, public text, private text, description text);'
			   ,
			   "insert into keys values (0, '', '', 'The public ring; unencrypted and insecure');"
			   ])

	def command(self, sql):
		if os.path.exists(self.path) == False:
			os.makedirs(self.path)
			f = open(self.name, 'w+', 0)
			f.close()

		r = dbExec(self.path + self.name, sql)
		return r

	def printRings(self):
		ringList = self.command('select ring, description from keys')
		x = ''
		count = 1
		for row in ringList:
			x.append('(' + str(count) + ') Ring', row[0], ' | ', row[1], '\n')
			count += 1
		return x

	def addRing(self, password, key, description):
		if self.user == 'guest':
			return False
		else:
			ringNumber = dbExec(self.gitfaceDB, 'select count(*) from keys;') + 1
			if verifyPassword(dbExec(self.path + 'users.db', 'select salt, passhash from users where username=' + self.user + ';'), password, maxTime = 0.1) == True:
				plainKey = RSA.importKey(key)
				publicKey = plainKey.publickey()
				privateKey = scrypt.encrypt(plainKey, password, maxtime = 0.1)
				dbExec(self.gitfaceDB, 'insert into keys values (?,?,?), ' + ringNumber + ', ' + privateKey + ', ' + publickey + ', ' + description + ';')
				for x in (password, plainKey, publicKey, privateKey):
					x = ''
				return True
			else:
				return False


class Entry(object):

	def __init__(
		self,
		timestamp=datetime.utcnow(),
		location=gitfaceDir + 'gitface.db',
		ring=0,
		):

		self.location = location  # Where the post lives, aka the absolute path to the stream database
		self.timestamp = timestamp
		self.ring = ring
		self.pubKey = \
			RSA.importKey(keyFetch(keyRing=ring))
		self.entryID = dbExec(self.location,
							  ['insert into stream values ('
							  + str(self.ring) + ", '', '', "
							  + self.timestamp + ');', 'select count(*) from stream;'])
		dbExec(self.location, "update stream set index=" + self.entryID + " where date=" + self.timestamp + " and ring=" + str(self.ring) + ";")

	def post(self, args):

		# args should be a string with alternating names and values separated by commas
		# it's an ugly imitation of named parameters, but it'll do

		encryptedargs = self.pubKey.encrypt(args, K)
		dbExec(self.location, 'update stream set data=' + encryptedargs + ' where date=' + self.entryID + ';')

	def read(self, ring, password):
		data = dbExec(self.location, "select * where index=" + str(self.entryID) + ";")
		decryptKey = RSA.importKey(scrypt.decrypt(dbExec(gitfaceDir + "keys.db", "select priKey from keys where ring=" + ring + ";"), password, maxtime = 0.1))
		plaintextData = decryptKey.decrypt(data)"""
