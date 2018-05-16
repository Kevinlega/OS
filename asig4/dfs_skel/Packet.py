###############################################################################
#
# Filename: Packet.py
# Author: Jose R. Ortiz and Kevin Legarreta
#
# Description:
# 	Packet creation support library for the DFS project. 

import json

class Packet:

	def __init__(self):
	
		self.commands = ["reg", "list", "put", "get", "dblks","remove","move","reg_user","admin","login","list_user", "updatePass", "removeuser"]
		self.packet = {}
		
	def getEncodedPacket(self):
		"""returns a seriliazed packet ready to send through the network.  
		First you need to build the packets.  See BuildXPacket functions."""

		return json.dumps(self.packet) 

	def getCommand(self):
		"""Returns the command type of a packet"""

		if "command" in self.packet:
			return self.packet["command"]
		return None

	def getAddr(self):
		"""Returns the IP address of a server""" 
		if "addr" in self.packet:
			return self.packet["addr"]
		return None
	def getPort(self):
		"""Returns the port number of a server"""
		if "port" in self.packet:
			return self.packet["port"]
		return None

	def DecodePacket(self, packet):
		"""Receives a serialized message and turns it into a packet object."""
		self.packet = json.loads(packet)	

	def BuildRegPacket(self, addr, port):
		"""Builds a registration packet"""
		self.packet = {"command": "reg", "addr": addr, "port": port}
		

	def BuildListPacket(self,user):
		"""Builds a list packet for file listing"""

		self.BuildCommand("list")
		self.packet["user"] = user

	def BuildListResponse(self, lfiles):
		"""Builds a list response packet"""

		self.packet = {"files": lfiles}	

	def getFileArray(self):
		"""Builds a list response packet"""

		if "files" in self.packet:
			return self.packet["files"]

	def BuildGetPacket(self, fname,name):
		"""Build a get packet to get fname."""
		self.BuildCommand("get")
		self.packet["fname"] = fname
		self.packet["user"] = name

	def BuildPutPacket(self, fname, fsize,digests,user):
		"""Builds a put packet to put fname and file size."""
		self.BuildCommand("put")
		self.packet["fname"] = fname
		self.packet["fsize"] = fsize
		self.packet["digests"] = digests
		self.packet["user"] = user

	def BuildDataBlockPacket(self, fname, block_list,user):
		"""Builds a data block packet. Contains the file name and the list of blocks for the file"""
		self.BuildCommand("dblks")
		self.packet["blocks"] = block_list
		self.packet["fname"] = fname
		self.packet["user"] = user

	def BuildGetDataBlockPacket(self, blockid,user):
		"""Builds a get data block packet. Usefull when requesting a data block to a data node."""

		self.BuildCommand("get")
		self.packet["blockid"] = blockid
		self.packet["user"] = user

	def getBlockID(self):
		"""Returns a the block_id from a packet."""
		return self.packet["blockid"]

	def getFileInfo(self):
		"""Returns the file info in a packet."""
		if "fname" in self.packet and "fsize" in self.packet:
			return self.packet["fname"], self.packet["fsize"] 

	def getFileName(self):
		"""Returns the file name in a packet."""
		if "fname" in self.packet:
			return self.packet["fname"] 

	def BuildGetResponse(self, metalist, fsize,digests):
		"""Builds a list of data node servers with the blocks of a file, and file size."""
		self.packet["servers"] = metalist
		self.packet["fsize"] = fsize
		self.packet["digests"] = digests

	def BuildPutResponse(self, metalist):
		"""Builds a list of data node servers where a file data blocks can be stored.
		I.E. a list of available data servers."""
		self.packet["servers"] = metalist

	def getDataNodes(self):
		"""Returns a list of data servers"""
		if "servers" in self.packet:
			return self.packet["servers"]
		return None

	def getDataBlocks(self):
		"""Returns a list of data blocks""" 
		if "blocks" in self.packet:
			return self.packet["blocks"]
		return None

	def BuildCommand(self, cmd):
		"""Builds a packet type"""
		if cmd in self.commands:
			self.packet = {"command": cmd}


	def BuildPutChunk(self, chunksize,user):
		"""Builds a put packet for data-node and sends the chunksize."""
		self.BuildCommand("put")
		self.packet["chunksize"] = chunksize
		self.packet["user"] = user

	def getChunkSize(self):
		"""Returns the chunksize in a packet."""
		if "chunksize" in self.packet:
			return self.packet["chunksize"]

	def BuildBlockSize(self, packet_size):
		"""Builds a put packet for data-node and sends the chunksize."""
		self.packet["SizeofPacket"] = packet_size

	def getPacketSize(self):
		"""Returns the chunksize in a packet."""
		if "SizeofPacket" in self.packet:
			return self.packet["SizeofPacket"]
	def getHash(self):
		"""Returns the hash of a file from the packet """
		if "digests" in self.packet:
			return self.packet["digests"]

	def BuildRemove(self,blockid,fname,user):
		"""Builds a remove file packet """
		self.BuildCommand("remove")
		self.packet["blockid"] = blockid
		self.packet["fname"] = fname
		self.packet["user"] = user
	
	def BuildMove(self,fname,new_name,user):
		"""Builds a move file packet """
		self.BuildCommand("move")
		self.packet["fname"] = tuple([fname,new_name])
		self.packet["user"] = user


	def RegisterUserPacket(self,user,password,salt,admin):
		"""Builds a register user packet """
		self.BuildCommand("reg_user")
		self.packet["password"] = password
		self.packet["user"] = user
		self.packet["salt"] = salt
		self.packet["admin"] = admin

	def GetNewUserInfo(self):
		"""Gets the info of a register new user packet """
		if "password" in self.packet and "salt" in self.packet and "user" in self.packet and "admin" in self.packet:
			return self.packet["user"], self.packet["password"], self.packet["salt"],self.packet["admin"]

	def CheckAdmin(self,user,password):
		"""Builds a check admin packet """
		self.BuildCommand("admin")
		self.packet["password"] = password
		self.packet["user"] = user


	def Login(self,user,password):
		"""Builds a login packet """
		self.BuildCommand("login")
		self.packet["password"] = password
		self.packet["user"] = user

	def GetUserInfo(self):
		"""Gets the info of a user packet """
		if "password" in self.packet and "user" in self.packet:
			return self.packet["user"], self.packet["password"]

	def ListUser(self):
		"""Builds a list user packet """
		self.BuildCommand("list_user")
	
	# def BuildListUserResponse(self, lusers):
	# 	"""Builds a list user response packet"""
	# 	"""Maybe la borro o la cambio para que sea distinta 
	# 	a la de files """

	# 	self.packet = {"users": lusers}	

	def UpdatePass(self, user,password):
		"""Builds a update password packet """
		self.BuildCommand("updatePass")
		self.packet["password"] = password
		self.packet["user"] = user

	def GetUser(self):
		"""Gets the user out of a packet """
		if "user" in self.packet:
			return self.packet["user"]

	def RemoveUser(self,user):
		"""Builds a remove user packet """
		self.BuildCommand("removeuser")
		self.packet["user"] = user 

	def SendKey(self,public_key):
		"""Builds a packet with a key object """
		self.packet["key"] = public_key

	def GetKey(self):
		"""returns the key object."""
		if "key" in self.packet:
			return self.packet["key"]