###############################################################################
#
# Filename: mv.py
# Author: Kevin Legarreta
#
# Description:
# 	Move client for the DFS

import socket
import sys

import getpass
from Packet import *
import Header

def usage():
	print("Usage: python %s <server>:<port>:<dfs file path> <new_filename>" %sys.argv[0]) 
	sys.exit(0)

def client(ip, mport,file_mv,new_filename):
	# Login
	name = Header.Login((ip,mport))

	# Contacts the metadata server and ask for list of files.

	data = Packet()
	data.BuildMove(file_mv,new_filename,name)
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
		# recieve the OK
		msg = sock.recv(1024)
		msg = msg.decode('utf-8')
		if msg == "NAK":
			raise
		elif msg == "NO":
			print("No such file in directory.")
		else:
			print("Moved the file")
		sock.close()

	except:
		sock.close()
		sys.exit("Error")


if __name__ == "__main__":

	if len(sys.argv) != 3:
		usage()

	file_mv = sys.argv[1].split(":")
	new_filename = sys.argv[2]

	# check file format of file on DFS or to be put on DFS
	check_format = new_filename.split("/")
	check_format = check_format[len(check_format)-1]
	if "." not in check_format:
		print("Error path name for DFS not in correct format. Should be path and filename.")
		print("Example: /home/file.txt")
		usage()

	if len(file_mv) == 2:
		ip = file_mv[0]
		port = 8000
		file_mv = file_mv[1]
	elif len(file_mv) == 3:
		ip = file_mv[0]
		port = int(file_mv[1])
		file_mv = file_mv[2]

	if not ip or not file_mv or not new_filename:
		usage()


	client(ip, port,file_mv,new_filename)
