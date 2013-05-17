# The GitFace module and API

import os
import sqlite3

# Convenience functions
# Connecting to a database and executing something
def dbExec(target, statements, encrypt):
	# target is the string of the absolte path to the database you want to write to
	# statements is a list of sql statements (make sure to add the ";" at the end; you aren't in Kansas anymore!)
	conn = sqlite3.connect(target)
	c = conn.cursor()
	for command in statements:
		c.execute(command)
	conn.commit()
	c.close()
	return c

###############
# Data Models #
###############
class Database(object):
	pass

class Stream(Database):
	def __init__(self, path, gitfaceDB = "gitface.db", keyDB = "keys.db", privateKey):
		self.path = path
		self.gitfaceDB = gitfaceDB
		self.keyDB = keyDB

		# Check if gitface database and tables are there; create if not
		if os.path.exists(self.path) == False:
			os.makedirs(self.path)
		f = open(self.path + self.gitfaceDB, "w+", 0)
		f.close()
		dbExec(self.path + self.name, ["create table if not exists stream (ring integer, metadata text, date real, body text);", "create table if not exists rings (ring integer, key text, description text);"])

		# Check if keys database and table exist, create if not
		f = open(self.path + self.keyDB, "w+", 0)
		f.close()
		dbExec(self.path + self.keyDB, ["create table if not exists keys (key text, description text);", "insert into keys values (0, '', 'The public ring; unencrypted and insecure');", "insert into keys values (1, " + privateKey + ", 'Your private data; do not share this key with anyone!');"])

	def command(self, sql):
		if os.path.exists(self.path) == False:
			os.makedirs(self.path)
			f = open(self.name, "w+", 0)
			f.close()

		dbExec(self.path + self.name, sql)
		return True

class Entry(object):
	def __init__(self, timestamp = datetime.utcnow(), location):
		self.location = location # Where the post lives, aka the absolute path to the stream database
		self.timestamp = timestamp
		self.metadata = {ring: 1}
		self.body = ""

	def update(args):
		# args should be a comma-seperated list of attribute/value pairs
		# it's an ugly imitation of named parameters, but it'll do
		for key in args.keys():
			if key.lower() == "ring":
				self.metadata["ring"] = args[key]
			elif key.lower() == "body":
				self.body == args[key]
			else:
				self.metadata[key.lower()] = args[key]

	def post(self, target = self.location):
		sql =
		dbExec(target, )

class EncryptedStream(object):
	def __init__(self, input):
		import