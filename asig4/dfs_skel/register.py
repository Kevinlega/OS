###############################################################################
#
# Filename: register.py
# Author: Kevin Legarreta
#
# Description:
# 	Move client for the DFS

import sys
from Packet import *
import Header
import getpass
import uuid
import hashlib
import socket


def usage():
	print("Usage: python %s <server>:<port> <new_user> <admin=1:user=0>" %sys.argv[0]) 
	sys.exit(0)

def client(ip, port,user,admin):
	#Check Admin privilege
	Header.Admin(ip,port)
	# insert user

	password = str(uuid.uuid4())
	password_copy = password
	password = password.encode('utf-8')
	salt = str(uuid.uuid4()).encode('utf-8')
	password = hashlib.md5( salt + password ).hexdigest()
	password = str(password)
	salt = str(salt)

	data = Packet()
	data.RegisterUserPacket(user,password,salt,admin)
	data = Header.encode(data)

	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((ip,port))
		#Send size of packet
		msg = Header.sendSize(sock,len(data))
		# if nak end else continue
		if msg == 'NAK':
			print("Metadata didn't recieve the packet size.")
			raise

		# Send packet
		sock.sendall(data)

		# Receive data from the server 
		recieved = sock.recv(1024)
		recieved = recieved.decode('utf-8')
		
		# If there is no error or duplicated is inserted
		if recieved == "DUP":
			print("Username taken.")
			raise
		elif recieved == "NAK":
			raise
		else:
			print("Successfully added user: %s with password %s."%(user,password_copy))
		sock.close()
	except:
		sys.exit("Error.")
		sock.close()

if __name__ == "__main__":

	if len(sys.argv) != 4:
		usage()

	server = sys.argv[1].split(":")

	if len(server) == 1:
		ip = server[0]
		port = 8000
		user = sys.argv[2]
		admin = int(sys.argv[3])

	elif len(server) == 2:
		ip = server[0]
		port = int(server[1])
		user = sys.argv[2]
		admin = int(sys.argv[3])

	if admin != 1 and admin != 0:
		print("admin must be 1 or 0.")
		usage()

	if not ip or not user:
		usage()

	client(ip, port,user,admin)