###############################################################################
#
# Filename: ls.py
# Author: Jose R. Ortiz and Kevin Legarreta
#
# Description:
# 	List client for the DFS
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
	# Login to server
	name = Header.Login((ip,port))

	# Contacts the metadata server and ask for list of files.

	data = Packet()
	data.BuildListPacket(name) # send the username to get the files of such user
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
	# Connect to server and send data

		sock.connect((ip, port))
		# encode the packet
		data = Header.encode(data)
		
		#Send size of packet
		msg = Header.sendSize(sock,len(data))
		# if size recieve continue else bye
		if msg == 'NAK':
			sys.exit("error")
		
		# Send Packet
		sock.sendall(data)

		# recieve incoming packet size
		size = Header.recieveSize(sock)
		# if size recieve continue else bye
		if not size:
			sock.sendall("NAK".encode('utf-8'))
		else:
			sock.sendall("OK".encode('utf-8'))

			# Receive data from the server and shut down
			data = Packet()
			recieved = Header.recvall(sock,size)
			recieved = recieved.decode('utf-8')
			# if recieve continue else bye
			if recieved == "NAK":
				sys.exit("Something went wrong")

			# decode the packet sent by server
			data.DecodePacket(recieved)
			# get the file list
			recieved = data.getFileArray()
			sock.close() # close connection

	except:
		sock.close()
		sys.exit("Bye")

	if not recieved:
		sys.exit("No files in the DFS.")
	else:
		for file, size in recieved:
			print('%s %s bytes'%(file, size))

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
