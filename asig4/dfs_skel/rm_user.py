###############################################################################
#
# Filename: rm_user.py
# Author: Kevin Legarreta
#
# Description:
# 	Remove user client for the DFS
#

import socket
import sys
import getpass
from Packet import *
import Header

def usage():
	print("Usage: python %s <server>:<port>:<username>" %sys.argv[0]) 
	sys.exit(0)

def client(ip, mport,user):

	# maybe import ls.py
	# Checks if the one running this is an Admin 

	Header.Admin(ip,mport)

	# Contacts the metadata server and ask for list of files. 
	# Of the user to remove

	# List request of user to remove
	data = Packet()
	data.BuildListPacket(user)
	data = Header.encode(data)

	try:
		# Connect to server and send data
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((ip,mport))

		#Send size of packet
		msg = Header.sendSize(sock,len(data))

		# if didnt recieve the size we leave
		if msg == 'NAK':
			print("metadata didn't recieve the packet size.")
			raise

		# Send packet
		sock.sendall(data)

		# recieve the size of the list response
		size = Header.recieveSize(sock)

		# if error recieving we leave else
		if not size:
			sock.sendall("NAK".encode('utf-8'))
			print("Error Didn't get list file size")
			raise
		else:
			sock.sendall("OK".encode('utf-8'))

			# Receive data from the server and shut down
			data = Packet()
			recieved = Header.recvall(sock,size)
			recieved = recieved.decode('utf-8')

			if recieved == "NAK":
				sys.exit("Something went wrong")

			data.DecodePacket(recieved)
			recieved = data.getFileArray() # retrieve the list of files
			sock.close() # close the socket

	except:
		sock.close()
		sys.exit("Bye")

	if not recieved:
		print("User %s has no files in the DFS."%user)
		print("Will now delete from user on metadata.")

	else:
		# if he had files delete them
		for file, size in recieved:
			# Run rm.py 
			# Contacts the metadata server and ask for list of nodes.
			data = Packet()
			data.BuildGetPacket(file,user)
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

				data.DecodePacket(recieved) #decode the packet
				
				# get node list size
				size = data.getPacketSize()
				# if size not recieved
				if not size:
					sock.sendall("NAK".encode('utf-8'))
					print("Size of the file chunk list not recived")
					raise
				# Notify we recieved the size
				sock.sendall("OK".encode('utf-8'))
				data = Packet()
				# Recieve the nodes
				recieved = Header.recvall(sock,size)
				recieved = recieved.decode('utf-8')
				data.DecodePacket(recieved)
				# gets the list
				data_nodes = data.getDataNodes()
				# miss flag
				missed = False

				# Go through all the nodes and delete every chunk
				for address,port,blockid in data_nodes:
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect((address,port))

					# Make a packet sending the block to remove
					# the user, filename is not needed but we 
					# keep it for reassurence

					p = Packet()
					p.BuildRemove(blockid,file,user)
					sock.sendall(Header.encode(p))

					# Recieve the answer to delete
					msg = sock.recv(1024)
					msg = msg.decode('utf-8')
					# if NAK Couldn't delete chunk if NO that chunk didnt exists
					# if OK we continue
					if msg == "NAK":
						print("Couldn't delete chunk of file.")
						missed= True
					elif msg == "NO":
						print("Chunk already missing")
						
					sock.close()

				if not missed: # if we deleted everything we remove
					# Contact the metadata when all chunks are deleted to remove file from system
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect((ip,mport))
					# build a remove file the blockid is not needed we are just reusing code ;)
					p = Packet()
					p.BuildRemove(blockid,file,user)
					p = Header.encode(p)

					#Send size of packet
					msg = Header.sendSize(sock,len(p))
					# if size recieve we continue if NAK we stop
					if msg == 'NAK':
						print("metadata didn't recieve the packet size.")
						raise

					# Send packet
					sock.sendall(p)
					sock.close()
			except:
				sock.close()
				sys.exit("Bye")
	try:
		# Contact the metadata to remove a user.
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((ip, mport))
		# Build a remove user packet
		p = Packet()
		p.RemoveUser(user)
		p = Header.encode(p)
		#Send size of packet
		msg = Header.sendSize(sock,len(p))
		# if size recieved we continue
		if msg == 'NAK':
			print("metadata didn't recieve the packet size.")
			raise

		# Send packet
		sock.sendall(p)

		# Receive data from the server 
		recieved = sock.recv(1024)
		recieved = recieved.decode('utf-8')
		
		# If there is no error we deleted else we didn't
		if recieved == "NO":
			print("Didn't remove user.")
			raise
		elif recieved == "NAK":
			print("Something went wrong")

		sock.close()
		
		print("Removed the user from the system along with his/her files.")

	except:
		sock.close()
		sys.exit("Bye")

if __name__ == "__main__":

	if len(sys.argv) != 2:
		usage()

	user = sys.argv[1].split(":")

	if len(user) == 2:
		ip = user[0]
		port = 8000
		user = user[1]
	elif len(user) == 3:
		ip = user[0]
		port = int(user[1])
		user = user[2]

	if not ip or not user:
		usage()

	client(ip, port,user)
