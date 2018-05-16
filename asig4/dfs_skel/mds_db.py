###############################################################################
#
# Filename: mds_db.py
# Author: Jose R. Ortiz and Kevin Legarreta
#
# Description:
# 	MySQL support library for the DFS project. Database info for the 
#       metadata server. Added querys to create more users, update password
#		check if admin, Get the salt to compute password, remove files, move a file
# 		And more.

import sqlite3

class mds_db:

	def __init__(self, db_name):
		self.c = None
		self.db_name=db_name
		self.conn = None
	
	def Connect(self):
		"""Connect to the database file"""
		try:
			self.conn = sqlite3.connect(self.db_name)
			self.c = self.conn.cursor()
			self.conn.isolation_level = None
			return 1
		except:
			return 0

	def Close(self):
		"""Close cursor to the database"""
		try:
			#self.conn.commit()
			self.c.close() 	
			return 1
		except:
			return 0
	
	def AddDataNode(self, address, port):
		"""Adds new data node to the metadata server
		   Receives IP address and port 
		   I.E. the information to connect to the data node
		"""
          
		query = """insert into dnode (address, port) values ("%s", %s)""" % (address, port)
		try:
			self.c.execute(query)
			return self.c.lastrowid 
		except sqlite3.IntegrityError as e: 
			# if the unique contraint fail return 0
			if "UNIQUE" in e.args[0]:
				return 0
			else:
				raise
			
	def CheckNode(self, address, port):
		"""Check if node is in database and returns name, address, port
                   for connection.
		"""
		query = """select nid from dnode where address="%s" and port=%s""" % (address, port)
		try:
			self.c.execute(query)
		except:
			return None
		return self.c.fetchone()[0]

	def GetDataNodes(self):
		"""Returns a list of data node tuples (address, port).  Usefull to know to which 
		   datanodes chunks can be send.
		"""

		query = """select address, port from dnode where 1"""
		self.c.execute(query)
		return self.c.fetchall()

	def InsertFile(self, fname, fsize,digests,user):
		"""Create the inode attributes.  For this project the name of the
		   file and its size. Basically checks if the user has a file
		   if not he gives the first file a number 1 as its id and so one 
		   from there. Since we now have a different primary key in the 
		   inode table we had to change the Autoincremet because in sqlite3
		   it only works on primary keys.
		"""
		query = """SELECT MAX(fid) + 1 FROM inode where owner=%d""" %user
		try:
			self.c.execute(query)
			result = self.c.fetchone()

			result = result[0]

			if not result:
				result = 1
			else:
				result = int(result)

			query = """insert into inode (fid, fname, fsize, hash,owner) values (%d,"%s", %s, "%s",%d)""" % (result,fname, fsize,digests,user)
		
			self.c.execute(query)
			return 1

		except:
			return 0
	
	def GetFileInfo(self, fname,user):
		"""Given a filename, if the file is stored in DFS
     		   return its filename id and fsize.  Internal use only.
		   Does not have to be accessed from the metadata server.
		"""
		query = """select fid, fsize,hash from inode where fname="%s" and owner=%d """ % (fname,user)
		try:
			self.c.execute(query)
			result = self.c.fetchone()
			return result[0], result[1],result[2]
		except:
			return None, None, None

	def GetFiles(self,user):
		"""Returns the attributes of the files stored in the DFS and owned by such user"""
		"""File Name and Size"""

		query = """select fname, fsize from inode where owner=%d"""%user ;
		self.c.execute(query)	
		return self.c.fetchall()
		

	def AddBlockToInode(self, fname, blocks,user):
		"""Once the Inode was created with the file's attribute
  	           and the data copied to the data nodes.  The inode is 
		   updated to point to the data blocks. So this function receives
                   the filename and a list of tuples with (node id, chunk id)
		"""
		fid, dummy1,digests= self.GetFileInfo(fname,user) 
		if not fid:
			return None
		for address, port, chunkid in blocks:
			nid = self.CheckNode(address, port)
			if nid:
				query = """insert into block (nid, fid, cid,owner) values (%s, %s, "%s",%d)""" % (nid, fid, chunkid,user)
				self.c.execute(query)
			else:
				return 0 
		return 1

	def GetFileInode(self, fname,user):
		"""Knowing the file name this function return the whole Inode information
	           I.E. Attributes and the list of data blocks with all the information to access 
                   the blocks (node name, address, port, and the chunk of the file).
		"""
		try:
			fid, fsize, digests = self.GetFileInfo(fname,user)
			if not fid:
				return None, None, None
			query = """select address, port, cid from dnode, block where dnode.nid = block.nid and block.fid=%s and block.owner=%d""" %(fid,user)
			self.c.execute(query)
			return fsize, self.c.fetchall(), digests
		except: 
			raise

	def RemoveFile(self,fname,user):
		"""Remove remove node list and file from database."""
		try:
			fid, fsize, digests = self.GetFileInfo(fname,user)
			if not fid:
				return 0
			query = """delete from block where fid=%d and owner=%d """%(fid,user)

	
			self.c.execute(query)

			query = """delete from inode where fname="%s" and owner=%d"""%(fname,user)
			self.c.execute(query)

			return 1
		except:
			return 0

	def MoveFile(self,fname,new_name,user):
		"""Moves file. Basically changes the name of the file."""
		try:	
			fid, fsize, digests = self.GetFileInfo(fname,user)
			if not fid:
				return 0
			print("here")
			query = """update inode set fname='%s' where fid=%d and owner=%d"""%(new_name,fid,user)
		
			self.c.execute(query)
			print("done")
			return 1
		except:
			return 0

	def InsertUser(self,user, password,salt,admin):
		"""Inserts new user to the database. """
		query = """insert into users (name,hash,salt,admin) values ("%s", "%s", "%s",%d)""" % (user, password,salt,admin)
		try:
			self.c.execute(query)
			return 1
		except:
			return 0

	def GetSalt(self,user):
		"""Retrieves the salt of a given user to compute the password """
		query ="""select salt from users where name="%s" """ % user
		try:
			self.c.execute(query)
			result = self.c.fetchone()
			return result[0]

		except:
			return None

	def Login(self, user,password):
		"""Basically checks if the password hashed matches to the uid give 
		and return the uid so that we can decide send the ok of the login."""
		query = """select uid from users where uid=%d and hash="%s" """ % (user,password)
		try:
			self.c.execute(query)
			result = self.c.fetchone()
			if result[0]:
				return 1
			else:
				return 0
		except:
			return None

	def CheckAdmin(self, user):
		"""Verifies the Admin priveledge of a given user."""
		query = """select admin from users where uid = %d """ % user
		try:
			self.c.execute(query)
			result = self.c.fetchone()
			if result[0] == 1:
				return 1
			else:
				return 0

		except:
			return None

	def GetUsers(self):
		"""Returns a list of users."""
		query = """select name from users where 1""" ;
		self.c.execute(query)	
		return self.c.fetchall()

	def updatePass(self,user,password):
		"""Changes the password of a given username."""
		query = """update users set hash="%s" where uid=%d"""%(password,user)
		try:
			self.c.execute(query)
			return 1
		except:
			return 0

	def GetUserID(self,user):
		"""Retrives the user id given a username """
		query = """select uid from users where name= "%s" """ %user
		try:
			self.c.execute(query)
			result = self.c.fetchone()
			result = int(result[0])
			if result:
				return result
			else:
				return 0

		except:
			return None

	def RemoveUser(self,user): 
		"""Removes a user from the database."""
		query = """delete from users where uid=%d"""%(user)
		try:
			self.c.execute(query)
			return 1
		except:
			return 0		