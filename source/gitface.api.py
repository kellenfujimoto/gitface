#!/usr/bin/python
# -*- coding: utf-8 -*-

# The GitFace module and API

import os
import sqlite3
from Crypto.PublicKey import RSA
from Crypto.Cipher import Blowfish
from Crypto.Random import random
import scrypt
from zlib import compress, decompress
from datetime import datetime

# Constants
# Might toss all of these into a configuration file. Once it gets too verbose.

gitfaceDir = os.path.expanduser(os.path.normcase('~/gitface'))  # Protect the Windows users' paths


# Convenience functions
# Connecting to a database and executing something

def dbExec(target, statements):

	# target is the string of the absolte path to the database you want to write to
	# statements is a list of sql statements (make sure to add the ";" at the end; you aren't in Kansas anymore!)

	conn = sqlite3.connect(target)
	c = conn.cursor()
	for command in statements:
		c.execute(command)
	conn.commit()
	c.close()
	return c  # Make dbExec() work with 'select' statements


# Fetxh a key from a database

def keyFetch(keyRing, keyDBPath=gitfaceDir + 'keys.db'):

	# Digs into key database and fetches either public or private key

	ringKey = dbExec(keyDBPath, ['from keys select public where ring is'
					  + str(keyRing) + ';'])
	return ringKey


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


# Class definitions

class User(object):

	def __init__(self, username='', path=gitfaceDir, password=''):
		if os.path.exists(path) == False:
			os.makedirs(path)
		self.location = path + 'users.db'
		dbExec(self.location,
			   'create table if not exists users (username text, salt text, passhash text, share text);'
			   )
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
		dbExec(self.location, 'insert into users values (?,?,?,?), '
			   + self.username + ',' + self.salt.hexdigest + ','
			   + self.passhash + ','
			   + self.sharePub + ';')


class Stream(object):

	""" Database stream of entries """

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
		plaintextData = decryptKey.decrypt(data)