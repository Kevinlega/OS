import hashlib
import getpass
import socket
import sys

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random


from Packet import *

def encode(p):
	''' Encodes the packet and makes it a bytes string to send'''
	p = Packet.getEncodedPacket(p)
	p = p.encode('utf-8')
	return p

def recvall(sock,size):
	''' Continues recieving until it has recieved everything'''
	msg = b''
	while len(msg)!= size:
		chunk = sock.recv(1024)
		msg += chunk
	return msg

def sendSize(sock,size):
	''' send the size of the block '''
	d = Packet()
	d.BuildBlockSize(size)
	sock.sendall(encode(d))
	msg = sock.recv(1024)
	msg = msg.decode('utf-8')
	return msg

def recieveSize(sock):
		''' recieve the size of the block  '''

		p = Packet()
		recieved = sock.recv(1024)
		recieved = recieved.decode('utf-8')
		p.DecodePacket(recieved)
		return p.getPacketSize()

def getChunkSize(fsize):
	''' Decides chuncksize of data to use, to change 
	size of chunks only need to change this function '''

	if fsize < 1024:	            # Handle Bytes (B)
		chunksize = fsize			# Same size
	elif fsize < 32768:			    # For less than 32 KB 2**15
		chunksize = 4				# Use 4K
	elif fsize < 33554432:	        # Handle KB 2**25
		chunksize = 32768    	    # 32 KB
	elif fsize < 1073741824:        # Handle MB 2**30
		chunksize = 131072   	    # 131 KB 2**17
	else:							# Handle GB and more
		chunksize = 524288   		# 524 KB 2**19
	return chunksize

def ComputeHash(path):
	"""Reads the file in chunks of 4096 bytes and returns 
	the hash of the file to store it on the database.
	Taken from one example on one link i provided."""

	BLOCKSIZE = 4096
	hasher = hashlib.md5()
	with open(path, 'rb') as afile:
	    buf = afile.read(BLOCKSIZE)
	    while len(buf) > 0:
	        hasher.update(buf)
	        buf = afile.read(BLOCKSIZE)
	return hasher.hexdigest()


def Admin(ip,mport):
	# Check if admin
	name = input("Admin username: ")
	while name == "":
		name = input("Try Again:")

	password = getpass.getpass(prompt="Password:  ")
	while password == "":
		password = getpass.getpass(prompt="Try Again:")

	# Send admin check request to metadata 
	data = Packet()
	data.CheckAdmin(name,password)
	data = encode(data)

	try:
		# Connect to server and send data
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((ip,mport))
		#Send size of packet

		msg = sendSize(sock,len(data))
		if msg == 'NAK':
			print("Metadata didn't recieve the packet size.")
			raise

		# Send packet
		sock.sendall(data)

		# recv answer
		recieved = sock.recv(1024)
		recieved = recieved.decode('utf-8')
		# if NOT then not user if no is not admin and NAK is error 
		# else is OK and we continue
		if recieved == "NOT":
			print("Not user.")
			raise
		elif recieved == "NAK":
			raise
		elif recieved == "NO":
			print("Not admin.")
			raise
		sock.close()
	except:
		sock.close()
		sys.exit("Bye")

def Login(address):
	# Login
	name = input("Username: ")
	while name == "":
		name = input("Try Again:")

	password = getpass.getpass(prompt="Password:  ")
	while password == "":
		password = getpass.getpass(prompt="Try Again:")

	""" Create a packet to send to the metadata server and see if 
	input is really user """
	data = Packet()
	data.Login(name,password)
	data = encode(data)

	try:
		# Connect to meta data server and send data
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(address)
		
		#Send size of packet
		msg = sendSize(sock,len(data))
		# If the message was recieved it won't be NAK and we can continue
		if msg == 'NAK':
			print("Metadata didn't recieve the packet size.")
			raise # basically is an error

		# Send packet
		sock.sendall(data)

		# recv answer
		recieved = sock.recv(1024)
		recieved = recieved.decode('utf-8') # decode bytes to string

		# We recive NO if not user and NAK if something went wrong
		#  If everything went OK it send OK and we continue
		if recieved == "NO":
			print("Not user.") 
			raise	# basically is an error
		elif recieved == "NAK":
			raise	# basically is an error

		sock.close()		# Close the socket

	except:
		sock.close()		# if error we close the socket
		sys.exit("Bye")		# Error can be either bad password, not user, or error in metadata
	return name


# For later
# def SendKey(sock,public_key):
# 	# Sends the key
	
# 	d = Packet()
# 	d.SendKey(public_key)
# 	sock.sendall(encode(d))

# def RecieveKey(sock):
# 	# Recieves the public key

# 	msg = sock.recv(1024)
# 	msg = msg.decode('utf-8')
# 	msg.DecodePacket()
# 	return msg.GetKey()

# def CreateKeys():
# 	# create Public/private key pair
# 	random_generator = Random.new().read
# 	return RSA.generate(4096, random_generator)

# def encrypt(public_key,text):
# 	# use public key to encrypt message
# 	return public_key.encrypt(text, 32)

# def decrypt(text,key):
# 	# uses the private key to decrypt a message
# 	return key.decrypt(text)

# def Sign(key,text,hash=None):
# 	# compute the signature and returns it
# 	if not hash:
# 		hash = SHA256.new(text).digest()
# 	return key.sign(hash, '')

# def Verify(public_key,signature,hash=None):
# 	# verify signature
# 	if not hash:
# 		hash = SHA256.new(text).digest()
	
# 	return public_key.verify(hash, signature)