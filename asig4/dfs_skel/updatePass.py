###############################################################################
#
# Filename: updatePass.py
# Author: Kevin Legarreta
#
# Description:
# 	Update Password client for the DFS
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
	# Login
	name = Header.Login((ip,port))

	# New Password
	password = getpass.getpass(prompt="New password:  ")
	while password == "":
		password = getpass.getpass(prompt="Try Again:")

	# Contacts the metadata server and ask to update password.

	data = Packet()
	data.UpdatePass(name,password)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
	# Connect to server and send data

		sock.connect((ip, port))
		# encode packet
		data = Header.encode(data)
		
		#Send size of packet
		msg = Header.sendSize(sock,len(data))
		if msg == 'NAK':
			sys.exit("error")
		
		# Send Packet
		sock.sendall(data)
		# recieve confirmation
		msg = sock.recv(1024)
		msg = msg.decode('utf-8')

		if msg == "NAK":
			print("ERROR")
		elif msg == "NO":
			print("Couldn't update.")
		elif msg == "OK":
			print("Password Changed.")

	finally:
		sock.close()

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
