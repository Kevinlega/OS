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

		# could also store randint(1,5) in a variable and call sleep
		time.sleep(randint(1,5))									# sleep for a random integer between 1 and 5

if __name__ == "__main__":
    main()	

# Could also make two local variables and call randint and use them in string creation and making mobile sleep. 