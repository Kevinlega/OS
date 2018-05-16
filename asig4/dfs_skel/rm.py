###############################################################################
#
# Filename: rm.py
# Author: Kevin Legarreta
#
# Description:
# 	Remove client for the DFS
#

import socket
import sys
import getpass
from Packet import *
import Header

def usage():
	print("Usage: python %s <server>:<port>:<dfs file path>" %sys.argv[0]) 
	sys.exit(0)

def client(ip, mport,file_rm):
	# Login
	name = Header.Login((ip,mport))

	# Contacts the metadata server and ask for list of files.

	data = Packet()
	data.BuildGetPacket(file_rm,name)
	data = Header.encode(data)

	try:
		# Connect to server and send data
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((ip,mport))

		#Send size of packet
		msg = Header.sendSize(sock,len(data))

		if msg == 'NAK':
			print("metadata didn't recieve the packet size.")
			raise

		# Send packet
		sock.sendall(data)

		# Receive data from the server 
		data = Packet()
		recieved = sock.recv(1024)
		recieved = recieved.decode('utf-8')
		
		# If there is no error response Retreive the data blocks
		if recieved == "NFOUND":
			print("File not found.")
			raise
		# Decode the list packet
		data.DecodePacket(recieved)
		
		# get size of list packet
		size = data.getPacketSize()
		# Size not recieved
		if not size:
			sock.sendall("NAK".encode('utf-8'))
			print("Size of the file chunk list not recived")
			raise
		# Send the OK to the meta that we recieved the size
		sock.sendall("OK".encode('utf-8'))

		# Recieve the list of nodes
		recieved = Header.recvall(sock,size)
		recieved = recieved.decode('utf-8')

		# retrieve data node list
		data = Packet()
		data.DecodePacket(recieved)
		data_nodes = data.getDataNodes()

		# missed flag to see if we missed a chunk
		missed = False

		# Go trough the whole data node list
		for address,port,blockid in data_nodes:
			# create a connection to the data nodes
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((address,port))

			# Make a packet sending the remove block request
			p = Packet()
			p.BuildRemove(blockid,file_rm,name)
			sock.sendall(Header.encode(p))

			# Recieve size of Packet
			msg = sock.recv(1024)
			msg = msg.decode('utf-8')

			# If we could delete this we recieve OK if not NAK id an error,
			# NO is that the Chunk wasn't there
			if msg == "NAK":
				print("Couldn't delete chunk of file.")
				# we missed a file therefore we can't delete the file from the 
				# server because we have something missing
				missed= True

			elif msg == "NO":
				# a chunk was already deleted
				print("Chunk already missing")
				
			sock.close()

		if not missed:
			# Contact the metadata when all chunks are deleted to remove file from system
			# This means we didnt miss any file
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((ip,mport))

			# Make a packet send it's size and request to delete the file from meta
			p = Packet()
			p.BuildRemove(blockid,file_rm,name)
			p = Header.encode(p)
			#Send size of packet
			msg = Header.sendSize(sock,len(p))
			# if OK we request the deletion of the file
			if msg == 'NAK':
				print("metadata didn't recieve the packet size.")
				raise

			# Send packet
			sock.sendall(p)
			# Recieve  comfirmation
			msg = sock.recv(1024)
			msg = msg.decode('utf-8')
			if msg == "OK":
				print("Removed the file.")
			else:
				print("Error")


			sock.close()

	except:
		sock.close()
		sys.exit("Bye")
	# Say we removed and leave	
	

if __name__ == "__main__":

	if len(sys.argv) != 2:
		usage()

	file_rm = sys.argv[1].split(":")

	# check file format of file on DFS or to be put on DFS
	check_format = file_rm[len(file_rm)-1].split("/")
	check_format = check_format[len(check_format)-1]
	if "." not in check_format:
		print("Error path name for DFS not in correct format. Should be path and filename.")
		print("Example: /home/file.txt")
		usage()

	if len(file_rm) == 2:
		ip = file_rm[0]
		port = 8000
		file_rm = file_rm[1]
	elif len(file_rm) == 3:
		ip = file_rm[0]
		port = int(file_rm[1])
		file_rm = file_rm[2]

	if not ip or not file_rm:
		usage()

	client(ip, port,file_rm)
