###############################################################################
#
# Filename: meta-data.py
# Author: Jose R. Ortiz and Kevin Legarreta
#
# Description:
# 	Does the jobs or send the data nodes to do the job in the database.
# 

from mds_db import *
from Packet import *
import sys
import socketserver
import os
import hashlib
import Header


# from Crypto.PublicKey import RSA
# from Crypto.Hash import SHA256
# from Crypto import Random




def usage():
	print("Usage: python %s <port, default=8000>" % sys.argv[0]) 
	sys.exit(0)

class MetadataTCPHandler(socketserver.BaseRequestHandler):

	def handle_reg(self, db, p):
		"""Register a new data node client to the DFS ACK if successfully REGISTERED
			NAK if problem, DUP if the IP and port already registered
		"""

		try:

			address,port= p.getAddr(),p.getPort()

			if db.AddDataNode(address, port): #fill:
				# if data node not in GetDataNodes()
				
				self.request.sendall("ACK".encode('utf-8'))

			else:
				# if data in GetDataNodes(), handle_get also checks the nodes
				self.request.sendall("DUP".encode('utf-8'))

		except:
			self.request.sendall("NAK".encode('utf-8'))

	def handle_list(self, db,p):
		"""Get the file list of a user from the database and send list to client"""
		# get user
		user = p.GetUser()

		try:
			# Retrieves the user id from the database
			user = db.GetUserID(user)
			# to be carefull we converted to int
			user = int(user)
			# builds a list response of file for that user
			p = Packet()
			p.BuildListResponse(db.GetFiles(user))
			# encodes the packet
			p = Header.encode(p)
			# send size to the list client
			msg = Header.sendSize(self.request,len(p))
			# if NAK client didnt recieve
			if msg == "NAK":
				print("Unable to send list packet")
				raise
			else: # continue sending
				self.request.sendall(p)

		except: # if error
			self.request.sendall("NAK".encode('utf-8'))	

	def handle_put(self, db, p):
		"""Insert new file into the database and send data nodes to save
		   the file.
		"""
	    
		# Get the file info the hash of the file and the user
		info = p.getFileInfo()
		digests = p.getHash()
		user = p.GetUser()

		try:
			# Retrieves the user id from the database
			user = db.GetUserID(user)
			# to be carefull we converted to int
			user = int(user)
			if user: # if we got confirmation we insert
				if db.InsertFile(info[0], info[1],digests,user):
					# send the ok of insert
					self.request.sendall("OK".encode('utf-8'))
					# create data node list packet
					p = Packet()
					p.BuildPutResponse(mds_db.GetDataNodes(db))
					# encode the packet
					p = Header.encode(p)
					
					# send the size of the packet
					msg = Header.sendSize(self.request,len(p))
					if msg == "NAK":
						print("Unable to send data node packet")
						raise
					# send the packet of data nodes
					self.request.sendall(p)

				else:
					self.request.sendall("DUP".encode('utf-8'))
			else:
				raise
		except: #if error
			self.request.sendall("NAK".encode('utf-8'))
	
	def handle_get(self, db, p):
		"""Check if file is in database and return list of
			server nodes that contain the file.
		"""

		# Get the file name from packet,user and then 
		# get the fsize,hash and array of chunk location
		fname = p.getFileName()
		user = p.GetUser()
		try:
			# Get the user id and converts it to int
			user = db.GetUserID(user)
			user = int(user)
			# if is a user we get the file info
			if user:
				fsize, metalist, digests = mds_db.GetFileInode(db,fname,user)

			if fsize and metalist:
				# Create Get response packet 
				p = Packet()
				p.BuildGetResponse(metalist, fsize,digests)
				p = Header.encode(p)
				
				#Send size of packet
				msg = Header.sendSize(self.request,len(p))
				if msg != 'NAK':
					# Send packet
					self.request.sendall(p)
				else:
					print("Error sending size to copy client.")
			else: # if file not in database
				self.request.sendall("NFOUND".encode('utf-8'))
		except: # error
			self.request.sendall("NAK".encode('utf-8'))

	def handle_blocks(self, db, p):
		"""Add the data blocks to the file inode"""

		# Get file name and blocks from packet,user
		fname, blocks = p.getFileName(), p.getDataBlocks()
		user = p.GetUser()
		try:
			user = db.GetUserID(user)
			user = int(user)
			# Fill code to add blocks to file inode
			if db.AddBlockToInode(fname, blocks,user):
				self.request.sendall("OK".encode('utf-8'))
			else:
				raise
		except:
			self.request.sendall("NAK".encode('utf-8'))

	def handle_remove(self,db,p):
		"""Remove the file of a user."""
		fname = p.getFileName()
		user = p.GetUser()
		try:
			# Get the user id and converts it to int
			user = db.GetUserID(user)
			user = int(user)
			if db.RemoveFile(fname,user): # removes
				self.request.sendall("OK".encode('utf-8'))
			else:
				raise
		except:
			self.request.sendall("NAK".encode('utf-8'))

	def handle_move(self,db,p):
		"""Moves the file."""
		fname = p.getFileName()
		user = p.GetUser()
		try:
			# Get the user id and converts it to int
			user = db.GetUserID(user)
			user = int(user)
			if db.MoveFile(fname[0],fname[1],user): # moves
				self.request.sendall("OK".encode('utf-8'))
			else:
				self.request.sendall("NO".encode('utf-8'))
		except:
			self.request.sendall("NAK".encode('utf-8'))


	def handle_admin(self,db,p):
		"""Check if user is admin """

		user, password = p.GetUserInfo()
		
		try:
			# Gets user salt for password
			salt = db.GetSalt(user)
			# Get the user id and converts it to int
			user = db.GetUserID(user)
			user = int(user)

			if salt: # if we got the salt we converted back to string
				salt = salt.replace('b\'',"")
				salt = salt.replace('\'',"")
				# make salt and password bytes objects
				password = password.encode('utf-8')
				salt = salt.encode('utf-8')
				# computed salted password hash
				password = hashlib.md5( salt + password ).hexdigest()
				password = str(password) # make it a string 

				if db.Login(user,password): # check if this admin is a user
					if db.CheckAdmin(user): # if its user check if its admin
						self.request.sendall("OK".encode('utf-8')) # send ok if admin
					else:
						self.request.sendall("NO".encode('utf-8')) # send No if not admin
				else:
					self.request.sendall("NOT".encode('utf-8')) # send NOT if not user
			else:
				raise # error
		except:
			self.request.sendall("NAK".encode('utf-8'))
		

	def handle_user_reg(self,db,p):
		"""Register a user """

		user, password,salt,admin = p.GetNewUserInfo()
		try:
			if db.InsertUser(user, password,salt,admin): # insert new user
				self.request.sendall("OK".encode('utf-8')) # send ok if chilling

			else:
				self.request.sendall("DUP".encode('utf-8')) # send Dup if already there
		except:
			self.request.sendall("NAK".encode('utf-8')) # Nak if error

	def handle_login(self,db,p):
		"""Login user """
		user, password = p.GetUserInfo()
		try:
			# Get salt to compute password 
			salt = db.GetSalt(user)

			if salt:
				# make it a string
				salt = salt.replace('b\'',"")
				salt = salt.replace('\'',"")
				# make password and salt bytes objects
				password = password.encode('utf-8')
				salt = salt.encode('utf-8')
				# compute hash of password and salt
				password = hashlib.md5( salt + password ).hexdigest()
				password = str(password)
				
				# get user id and make it int
				user = db.GetUserID(user)
				user = int(user)

				if db.Login(user,password): # try to login
					self.request.sendall("OK".encode('utf-8')) # ok if user
				else:
					self.request.sendall("NO".encode('utf-8')) # NO if not user

			else: # NAK if error
				raise
		except:
			self.request.sendall("NAK".encode('utf-8'))
		

	def handle_list_user(self,db,p):
		"""Get a list of users from the database and send list user to client"""
		try:
			# make a response packet
			p = Packet()
			p.BuildListResponse(db.GetUsers())
			p = Header.encode(p)
			# send the size
			msg = Header.sendSize(self.request,len(p))
			# if recieved continue else stop
			if msg == "NAK":
				print("Size of packet lost")
			else: # send the list
				self.request.sendall(p)

		except: # error
			self.request.sendall("NAK".encode('utf-8'))

	def handle_updatePass(self,db,p):
		""""Update users password """
		user, password = p.GetUserInfo()
		try:
			# Get salt for the user
			salt = db.GetSalt(user)
			if salt:
				# make it string
				salt = salt.replace('b\'',"")
				salt = salt.replace('\'',"")
				# make password and salt bytes
				password = password.encode('utf-8')
				salt = salt.encode('utf-8')
				# compute new password
				password = hashlib.md5( salt + password ).hexdigest()
				password = str(password)
				# get user id and make it int
				user = db.GetUserID(user)
				user = int(user)

				if db.updatePass(user,password): #update the password
					self.request.sendall("OK".encode('utf-8'))# ok if changed
				else:
					self.request.sendall("NO".encode('utf-8')) # no ifcouldnt
			
			else:
				raise # NAK if error
		except:
			self.request.sendall("NAK".encode('utf-8'))

	def handle_rm_user(self,db,p):
		"""Remove a user from the database."""
		user = p.GetUser()
		try:
			# Get user id and make it int
			user = db.GetUserID(user)
			user = int(user)
			
			if db.RemoveUser(user): # remove
				self.request.sendall("OK".encode('utf-8')) # send the ok
			else:
				self.request.sendall("NO".encode('utf-8')) # send the couldn't
		except:
			self.request.sendall("NAK".encode('utf-8'))

	def handle(self):
		global key
		# Exchange of keys

		other_key = Header.RecieveKey(self.request)
		Header.SendKey(key.publickey())
	
		# Recieve the packetsize
		size = Header.recieveSize(self.request)
		# if gotten we send ok if not NAk
		if not size:
			self.request.sendall("NAK".encode('utf-8'))
		else:
			self.request.sendall("OK".encode('utf-8'))

			if os.path.isfile("dfs.db"): # database created we connect else we exit
				# Establish a connection with the local database
				db = mds_db("dfs.db")
				db.Connect()
			else:
				sys.exit("Database isn't created.")

			# Define a packet object to decode packet messages
			p = Packet()

			# recieve full message from the list, data-node, or copy clients
			msg = Header.recvall(self.request,size)
			# Decode utf-8
			msg = msg.decode('utf-8')
			# print msg and type
			print(msg, type(msg))
			
			# Decode the packet received
			p.DecodePacket(msg)
		
			# Extract the command part of the received packet
			cmd = p.getCommand()

			# Invoke the proper action 
			if   cmd == "reg":
				# Registration client
				self.handle_reg(db, p)

			elif cmd == "list":
				# Client asking for a list of files
				data = self.handle_list(db,p)

			elif cmd == "put":
				# Client asking for servers to put data
				self.handle_put(db, p)

			elif cmd == "get":
				# Client asking for servers to get data
				self.handle_get(db, p)

			elif cmd == "dblks":
				# Client sending data blocks for file		
				self.handle_blocks(db, p)

			elif cmd == "remove":
				# Client want's to remove
				self.handle_remove(db,p)

			elif cmd == "move":
				# client wants to rename file and move it
				self.handle_move(db,p)

			elif cmd == "admin":
				# client to check admin
				self.handle_admin(db,p)

			elif cmd == "reg_user":
				# client to register user
				self.handle_user_reg(db,p)

			elif cmd == "login":
				# client to login
				self.handle_login(db,p)

			elif cmd == "list_user":
				# client to list users
				self.handle_list_user(db,p)

			elif cmd == "updatePass":
				#client to update pass
				self.handle_updatePass(db,p)

			elif cmd == "removeuser":
				# client to remove user
				self.handle_rm_user(db,p)

			db.Close()

if __name__ == "__main__":
    HOST, PORT = "", 8000

    if len(sys.argv) > 1:
    	try:
    		PORT = int(sys.argv[1])
    	except:
    		usage()
  # For later
  #   try:
  #   	# import the key
		# with open('priv_key.pem','r') as file:
		# 	key = RSA.importKey(file.read().encode('utf-8'))		

  #   except:
  #   	# create key and save
  #   	key = Header.CreateKeys()
  #   	with open('priv_key.pem','w') as file:
		# 	file.write(key.exportKey().decode('utf-8'))

    server = socketserver.TCPServer((HOST, PORT), MetadataTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
