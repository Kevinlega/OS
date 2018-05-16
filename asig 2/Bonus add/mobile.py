##### BONUS ####
# Kevin Legarreta				801-14-3452

import sys															# For argument parsing
import socket 														# For socket creation
from random import randint											# For random integer
from threading import Thread 										# Create Thread
import time									    					# To make thread sleep

def main():

	HOST = sys.argv[2]												# Host from system input 
	PORT = int(sys.argv[3])											# Port from system input converted to string
	connection = (HOST,PORT)										# Tuple that holds the connection we need to make

	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 			# Create socket connection

	while True:														# endless loop
		string = ""													# start every cycle with empty string
		string = str(sys.argv[1]) + ":" + str(randint(1,5))			# Add mobile id from system input a : 
																	# and a random integer for sleep job
		string = bytes(string,"ascii")								# Since python3 we need to change to bytes

		# print(string)												# If you want to see the string being sent to scheduler 								
		s.sendto(string,connection)								    # send message to scheduler (message = string)
		print("Waiting for message from the server:")
		s.settimeout(300)											# If after 5 min no answer kill this process 
																	# only works for small Nth case if increase Nth case
																	# must grow
		data, addr = s.recvfrom(1024)								
		s.settimeout(None)											# Don't timeout
		print("Message here: %s"%data)

if __name__ == "__main__":
    main()	

