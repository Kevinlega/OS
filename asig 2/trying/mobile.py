import sys										# For argument parsing
import socket 									# For socket creation
from random import randint						# For random integer
from threading import Thread 					# Create Thread
import time									    # To make thread sleep

# Create connection to the socket
def socketcreate(host, port):
	# s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	# s.connect((host,port))
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	while True:
		string = ""
		# s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		string = str(sys.argv[1]) + ":" + str(randint(1,5))
		string = bytes(string,"ascii")
		print(string)
		try:
			s.sendto(string,(host,port))
		except socket.error:
			print("fail")
		
		# data, server = s.recvfrom(1024)
		# if not data: break
		# print(str(data))
		
		# time.sleep(randint(1,5))
		time.sleep(5)
		# print("cycle %d"%i)
		# s.close()

	# randint(1,50) 

def main():
	
	# Create connection to the socket
	# socketcreate(sys.argv[2], int(sys.argv[3]))	

	# Create one threads to send jobs
	# Number of thread not needed but will be equal to mobile ID	
	thread = Thread(target = socketcreate, args=(sys.argv[2], int(sys.argv[3])))
	thread.start()






if __name__ == "__main__":
    main()	







