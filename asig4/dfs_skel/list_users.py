###############################################################################
#
# Filename: list_users.py
# Author: Kevin Legarreta
#
# Description:
# 	List user client for the DFS
#

import socket
import sys
import getpass

from Packet import *
import Header 

def usage():
	print("Usage: python %s <server>:<port, default=8000>" %sys.argv[0]) 
	sys.exit(0)

def client(ip, port):

	# Check Admin priviledge
	Header.Admin(ip,port)

	# Contacts the metadata server and ask for list of files.

	data = Packet()
	# build a list user request packet
	data.ListUser()
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		# Connect to server and send data

		sock.connect((ip, port))
		# encode the packet
		data = Header.encode(data)
		
		#Send size of packet
		msg = Header.sendSize(sock,len(data))
		if msg == 'NAK':
			sys.exit("error")
		
		# Send Packet
		sock.sendall(data)

		# recieve incoming packet size
		size = Header.recieveSize(sock)

		if not size:
			sock.sendall("NAK".encode('utf-8'))
			raise
		else:
			sock.sendall("OK".encode('utf-8'))

			# Receive data from the server and shut down
			data = Packet()
			recieved = Header.recvall(sock,size)
			recieved = recieved.decode('utf-8')
			# if nak error else continue
			if recieved == "NAK":
				sys.exit("Something went wrong")
			# get the fi
			data.DecodePacket(recieved)
			# reusing code we retrive the users stored in a packet
			# that hold files
			recieved = data.getFileArray()
			sock.close()

	except:
		sock.close()
		sys.exit("Bye")

	if not recieved:
		# should never happen because if you get here at least the admin is the user
		sys.exit("No users in the DFS.")

	else:
		count = 1
		#print the user with his id
		for user in recieved:
			print('User:%s, uid:%s'%(user[0],count))
			count +=1

if __name__ == "__main__":

	if len(sys.argv) < 2:
		usage()

	ip = None
	port = None 
	server = sys.argv[1].split(":")
	if len(server) == 1:
		ip = server[0]
		port = 8000
	elif len(server) == 2:
		ip = server[0]
		port = int(server[1])

	if not ip:
		usage()

	client(ip, port)