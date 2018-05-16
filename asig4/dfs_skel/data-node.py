###############################################################################
#
# Filename: data-node.py
# Author: Jose R. Ortiz and Kevin Legarreta
#
# Description:
# 	data node server for the DFS, added remove chunks 

from Packet import *
import Header 
import sys
import socket
import socketserver
import uuid
import os

def usage():
	print("Usage: python %s <server> <port> <data path> <metadata port,default=8000>" % sys.argv[0]) 
	sys.exit(0)

def register(meta_ip, meta_port, data_ip, data_port):
	"""Creates a connection with the metadata server and
	   register as data node
	"""

	try:
		# Establish connection
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((meta_ip,meta_port))
		
		# Won't change until data node registers
		response = "NAK"
		
		# Build the register request fot the metadata
		data = Packet()
		data.BuildRegPacket(data_ip, data_port)
		data = Header.encode(data)

		#Send size of packet
		msg = Header.sendSize(sock,len(data))
		# if didnt recieve the size we leave else continue
		if msg == 'NAK':
			raise

		# Send Packet
		while response == "NAK":
			# Keep sending until registered
			sock.sendall(data)
			response = sock.recv(1024)
			response = response.decode('utf-8')
			# if Duplicated we ok we break the cicle
			if response == "DUP":
				print("Duplicate Registration")
			# continue trying until we get the OK
			elif response == "NAK":
				print("Registratation ERROR")

	except:
		sock.close()
		sys.exit("Couldn't connect/register to metadata.")
	

class DataNodeTCPHandler(socketserver.BaseRequestHandler):

	def handle_put(self, p):

		"""Receives a block of data from a copy client, and 
		   saves it with an unique ID.  The ID is sent back to the
		   copy client.
		"""	
		name = p.GetUser() # gets the user from the packet
		self.request.sendall("OK".encode('utf-8')) # notify we recieved the packet with size

		# recv all the data block that was sent
		byte = Header.recvall(self.request,p.getChunkSize())

		# Generates an unique block id.
		blockid = str(uuid.uuid1())

		# get the path name to the new data block
		# Data node path with username before the block id
		# DATA_PATH/userblockid
		filename = os.path.join(DATA_PATH,str(name) + blockid)

		# Open the file for the new data block.  
		with open(filename, 'wb') as file:
			# write the bytes to the new file
			file.write(byte)
		# send the blockid to the copy client
		self.request.sendall(blockid.encode('utf-8'))

	def handle_get(self, p):
		
		# Get the block id from the packet
		blockid = p.getBlockID()
		# Get user from packet
		name = p.GetUser()

		# merge the DATA_PATH to the filename to know which data block to send
		filename = os.path.join(DATA_PATH,str(name) +blockid)

		# read all the file with size getsize
		chunksize = os.path.getsize(filename)
	
		# used to read the file		
		byte = ''
		# open the file
		with open(filename,'rb') as file: 
			# read all the file
			byte = file.read(chunksize)

			# Send byte size
			msg = Header.sendSize(self.request,len(byte))
			if msg == "OK":
				# if ok we send
				self.request.sendall(byte)
			else:
				# we do nothing
				self.request.close()

	def handle_remove(self,p):

		# Get the block id from the packet
		blockid = p.getBlockID()
		user = p.GetUser() # get user from packet
		# merge the DATA_PATH to the filename 
		filename = os.path.join(DATA_PATH,str(user)+blockid)
		
		# remove the chunk
		try:
			if os.path.isfile(filename): # if it exists
				os.remove(filename)		# remove it
				self.request.sendall("OK".encode('utf-8')) # senf the OK
			else:
				self.request.sendall("NO".encode('utf-8')) # if not we say that it was missing
		except:
			self.request.sendall("NAK".encode('utf-8')) # Something went wrong


	def handle(self):
		# Recieve the msg and decode it
		msg = self.request.recv(1024)
		msg = msg.decode('utf-8')

		print(msg, type(msg)) # print the request to the data node
		# decode the packet
		p = Packet()
		p.DecodePacket(msg)
		# get the command to execute
		cmd = p.getCommand()
		
		# decides what to do
		if cmd == "put":
			self.handle_put(p)
		elif cmd == "get":
			self.handle_get(p)
		elif cmd == "remove":
			self.handle_remove(p)
		
if __name__ == "__main__":

	META_PORT = 8000
	if len(sys.argv) < 4:
		usage()

	try:
		HOST = sys.argv[1]
		PORT = int(sys.argv[2])
		DATA_PATH = sys.argv[3]

		if len(sys.argv) > 4:
			META_PORT = int(sys.argv[4])

		if not os.path.isdir(DATA_PATH):
			print("Error: Data path %s is not a directory." % DATA_PATH)
			usage()
	except:
		usage()


	register("localhost", META_PORT, HOST, PORT)
	server = socketserver.TCPServer((HOST, PORT), DataNodeTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
	server.serve_forever()
