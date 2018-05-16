###############################################################################
#
# Filename: copy.py
# Author: Jose R. Ortiz and Kevin Legarreta
#
# Description:
# 	Copy client for the DFS, hashes the into file and from file to verify integrity.
#   Also only gets the Logged in users files not every one elses files.

import hashlib
import getpass
import socket
import sys
import os.path

from Packet import *
import Header

def usage():
	print("Usage:\n\tFrom DFS: python %s <server>:<port>:<dfs file path> <destination file>\n\tTo   DFS: python %s <source file> <server>:<port>:<dfs file path>" % (sys.argv[0], sys.argv[0]))
	sys.exit(0)

def copyToDFS(address, fname, path):
	""" Contact the metadata server to ask to copy file fname,
	    get a list of data nodes. Open the file in path to read,
	    divide in blocks and send to the data nodes. 
	"""

	# Login
	name = Header.Login(address)

	# Compute hash
	digests = Header.ComputeHash(path)

	# Create a connection to the data server to send the file put request
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(address)

		# Get file size
		fsize = os.path.getsize(path)

		# Create a Put packet with the fname and the file size,
		# and sends it to the metadata server

		p = Packet()
		p.BuildPutPacket(fname, fsize,digests,name)

		# Encode it to send
		p = Header.encode(p)

		#Send size of packet and recieves the OK
		msg = Header.sendSize(sock,len(p))
		if msg == 'NAK':
			print("error")

		# Send Packet
		sock.sendall(p)

		# Recieve if database entry was successfull
		recieved = sock.recv(1024)
		recieved = recieved.decode('utf-8')
		# if duplicated or not able to enter we exit
		if recieved == "DUP":
			print("The file already exists.")
			raise
		elif recieved == "NAK":
			print("Couldn't insert to db.")
			raise
		# we recieve the size of the node list
		size = Header.recieveSize(sock)
		
		# if suceesfull we send the OK to recieve it 
		if not size:
			sock.sendall("NAK".encode('utf-8'))
			print("Something went wrong contacting metadata")
			raise
		else:
			sock.sendall("OK".encode('utf-8'))
			recieved = Header.recvall(sock,size)
		
		sock.close()
	# If no error or file exists
	# Get the list of data nodes.
	# Divide the file in blocks
	# Send the blocks to the data servers

	except:
		sock.close()
		sys.exit("Bye")
		
	# If we made it here we have a node list
	p = Packet()
	# we decode this packet
	recieved = recieved.decode('utf-8')
	p.DecodePacket(recieved)
	
	# get data nodes from packet
	dnodes = p.getDataNodes()

	# Holds the list of dnodes entry in order
	metalist = []
	# Position in where we send first
	x = 0

	# Determine the chunksize to send file in KB
	chunksize = Header.getChunkSize(fsize)

	# Read file
	with open(path,'rb') as file:
		# Read a chunk of file
		byte = file.read(chunksize)
		size = len(byte)
		error = False

		try:
			# executes until the file is read
			while byte:
				# Connect to the data nodes 
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				# connect to data node in position x
				sock.connect(tuple(dnodes[x]))
				
				# Send the size of the bytes to send
				dummy = Packet()

				dummy.BuildPutChunk(size,name)
				sock.sendall(Header.encode(dummy))

				msg = sock.recv(1024)
				msg = msg.decode('utf-8')

				# if it was recieved we send the bytes
				if msg == "OK":
					# Send file
					sock.sendall(byte)
					
					# Recv the blockid
					blockid = sock.recv(1024)
					
					# Holds the list of dnodes order
					metalist.append([dnodes[x][0],dnodes[x][1],blockid.decode('utf-8')])
					
					# Update the nodes pointer
					x = (x+1)%len(dnodes)

					# Done recving so we end sock
					sock.close()

					# Update the bytes and the size 
					byte = file.read(chunksize)
					size = len(byte)
				else:
					# exit if something bad happened
					print("A chunk went rogue. Metalist to remove %s "%metalist)
					raise
		except:
			sock.close()
			print("Remove the file, something wrong.")
			# we still will put the file chunks in the meta so we can delete it
			# so we continue

		# Notify the metadata server where the blocks are saved.
		# In case there was error so that it can be removed and 
		# if no error to know where the files are.

		p = Packet()
		p.BuildDataBlockPacket(fname, metalist,name)
		p = Header.encode(p)

		try:
			# connect to the meta data
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect(address)
			
			#Send size of packet
			msg = Header.sendSize(sock,len(p))
			# if could recieve the size we say error
			if msg == 'NAK':
				print("Metadata didn't recieve the packet size.")
				raise
			# send the chunks
			sock.sendall(p)
			msg = sock.recv(1024)
			msg = msg.decode('utf-8')
			if msg == "OK":
				print("Saved chunks to metadata")
			else:
				raise
			# close socket
			sock.close()
		
		except:
			sock.close()
			sys.exit("Couldn't save the chunks to the metadata")
	
def copyFromDFS(address, fname, path):
	""" Contact the metadata server to ask for the file blocks of
    the file fname.  Get the data blocks from the data nodes.
    Saves the data in path.
	"""
   	# Contact the metadata server to ask for information of fname
	name = Header.Login(address)
	# Build get chunk location packet
	data = Packet()
	data.BuildGetPacket(fname,name)
	data = Header.encode(data)

	try:
		# Connect to server and send data
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(address)

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

		data.DecodePacket(recieved)
		
		# get node list size
		size = data.getPacketSize()
		if not size:
			sock.sendall("NAK".encode('utf-8'))
			print("Size of the file chunk list not recived")
			raise

		# Send OK so it knows we recieved the size
		sock.sendall("OK".encode('utf-8'))
		# recieve the data nodes
		recieved = Header.recvall(sock,size)
		recieved = recieved.decode('utf-8')
		# Retrieve the packet
		data = Packet()
		data.DecodePacket(recieved)

		# Get data nodes and hash
		data_nodes = data.getDataNodes()
		original_digests = data.getHash()

		# Open the output file
		with open(path,'wb') as file:
			# go through the whole list and retrieve every chunk
			for address,port,blockid in data_nodes:
				# connect to data node
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.connect((address,port))

				# Make a packet sending the blockid and username
				p = Packet()
				p.BuildGetDataBlockPacket(blockid,name)
				# send it
				sock.sendall(Header.encode(p))

				# Recieve size of Packet with the file chunk
				size = Header.recieveSize(sock)
				# Send NAK if didn't recieve size
				if not size:
					sock.sendall("NAK".encode('utf-8'))
					print("Size of Packet not recieved")
					raise
				else:
					# send the OK
					sock.sendall("OK".encode('utf-8'))
					# recieve the file
					byte = Header.recvall(sock,size)
					# write the chunk
					file.write(byte)

					# close the socket connection
					sock.close()
		# Get the hash of the new file
		new_file_digests = Header.ComputeHash(path)

		# compare the old hash to the retrieved
		if original_digests != new_file_digests:
			print("Not original file")
			raise

		print("The file is the same as the original.")
		sock.close()

	except:
		sock.close()
		sys.exit("Error. Bye")


if __name__ == "__main__":
	if len(sys.argv) < 3:
		usage()

	file_from = sys.argv[1].split(":")
	file_to = sys.argv[2].split(":")

	# check file format of file on DFS or to be put on DFS
	check_format = file_to[len(file_to)-1].split("/")
	check_format = check_format[len(check_format)-1]
	if "." not in check_format:
		print("Error path name for DFS not in correct format. Should be path and filename.")
		print("Example: /home/file.txt")
		usage()

	if len(file_from) > 1:
		ip = file_from[0]
		port = int(file_from[1])
		from_path = file_from[2]
		to_path = sys.argv[2]

		if os.path.isdir(to_path):
			print("Error: path %s is a directory.  Please name the file." %to_path)
			usage()

		copyFromDFS((ip, port), from_path, to_path)

	elif len(file_to) > 2:
		ip = file_to[0]
		port = int(file_to[1])
		to_path = file_to[2]
		from_path = sys.argv[1]



		if os.path.isdir(from_path):
			print("Error: path %s is a directory.  Please name the file." %from_path)
			usage()
		
		if not os.path.isfile(from_path):
			print("The file in path %s can't be read."%from_path)
			usage()

		copyToDFS((ip, port), to_path, from_path)