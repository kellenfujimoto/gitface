# The GitFace module and API

import os
import sqlite3
from Crypto.PublicKey import RSA
import zlib

# Constants
# Might toss all of these into a configuration file. Once it gets too verbose.
gitfaceDir = os.path.expanduser(os.path.normcase("~/gitface")) # Protect the Windows users' paths

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
	return c # Make dbExec() work with 'select' statements

def keyFetch(keyRing, keyDBPath = gitfaceDir + "keys.db", kind):
	# Digs into key database and fetches either public or private key
	if kind is "private":
		ringKey = dbExec(keyDBPath, ["from keys select private where ring is" + str(keyRing) + ";"])
	else:
		ringKey = dbExec(keyDBPath, ["from keys select public where ring is" + str(keyRing) + ";"])
	return ringKey

# Class definitions

class Stream(object):
	""" Database stream of entries """
	def __init__(self, path = gitfaceDir, gitfaceDB = "gitface.db", keyDB = "keys.db", privateKey):
		self.path = path
		self.gitfaceDB = gitfaceDB
		self.keyDB = keyDB

		# Check if gitface database and tables are there; create if not
		if os.path.exists(self.path) == False:
			os.makedirs(self.path)
		f = open(self.path + self.gitfaceDB, "w+", 0)
		f.close()
		dbExec(self.path + self.name, ["create table if not exists stream (ring integer, data text, date real);", "create table if not exists rings (ring integer, priKey text, pubKey text, description text);"])

		# Check if keys database and table exist, create if not
		f = open(self.path + self.keyDB, "w+", 0)
		f.close()
		# Need to generate public and private keys for ring 1
		dbExec(self.path + self.keyDB, ["create table if not exists keys (ring text, public text, description text);", "insert into keys values (0, '', 'The public ring; unencrypted and insecure');", "insert into keys values (1, " + pubKey + ", 'Your private data; do not share the private key with anyone!')"])

	def command(self, sql):
		if os.path.exists(self.path) == False:
			os.makedirs(self.path)
			f = open(self.name, "w+", 0)
			f.close()

		r = dbExec(self.path + self.name, sql)
		return r

class Entry(object):
	def __init__(self, timestamp = datetime.utcnow(), location, ring = 1):
		self.location = location # Where the post lives, aka the absolute path to the stream database
		self.timestamp = timestamp
		self.ring = ring
		self.pubKey = RSA.RSAImplimentation.importKey(keyFetch(keyRing = ring))
		self.entryID = dbExec(self.location, ["insert into stream values (" + str(self.ring) + ", '', " + self.timestamp + ");"])

	def post(args):
		# args should be a tuple with alternating names and values
		# it's an ugly imitation of named parameters, but it'll do
		data = self.pubKey.encrypt(zlib.compress(args, 9), K)
		dbExec(self.location, ["update stream set data=" + str(data) + " where timestamp=" + self.timestamp + ";"])
		delattr(args)
		return True