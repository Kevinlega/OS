import sys
import socket
from random import randint
from threading import Thread, Lock, Semaphore
import time

class Queue:
	def __init__(self):
		self.buffer =[]
		self.length = 0
	def enqueue(self,job):
		self.buffer.append(job)
		self.length +=1
	def dequeue(self):
		self.buffer.pop(0)
		self.length -=1




def jobcreate(host, port):

	
	global jobs_in_buffer


	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	s.bind((host,port))
	# s.listen(5) # let 5 connection be waiting
	# con, addr = s.accept()
	# print("conected by %s" %str(addr))
	data = ""
	global MAX_JOBS
	MAX_JOBS = 10
	index = 0
	while True:
	
		# try:
		# 	con, addr = s.accept()
		# 	print("conected by %s" %str(addr))
		# except:
		# 	continue

		# while not data:
			# data = con.recv(1024)
		data, addr = s.recvfrom(1024)
		x = str(addr)
		print("esto es el addr "+x)

		# con.sendall(data)
		global lock
		lock.acquire()
		jobs_in_buffer +=1
		semaphore.release()
		buff.append(data)
		print(buff)
		print(index)
		index +=1
		print("waking up")
		# condition.notify()

		lock.release()
		
		MAX_JOBS -=1
		if MAX_JOBS == 0: 
			break
		
		# con.sendall(data)
	
	s.close()
		

	print(buff)
	print("exit producer")

	# recvfrom (string address)
def consumejob():
	
	global lock
	global jobs_in_buffer
	global MAX_JOBS
	semaphore.acquire()
	while True:
		
		if jobs_in_buffer > 0:
			# condition.acquire()
			lock.acquire()
			data = buff.pop(0)
			jobs_in_buffer -=1
			# condition.release()
			lock.release()
			# print(data)
			data = str(data)
			data = data.replace("b\'","")
			data = data.replace("\'","")
			data = data.split(":")
			try:
 				mobilejobs[data[0]] = int(mobilejobs[data[0]]) + int(data[1])
			except:
				mobilejobs[data[0]] = int(data[1])
			print("sleeping %s from mobile job %s"%(data[1],data[0]))
			time.sleep(int(data[1]))
			print("done sleeping %s from mobile job %s"%(data[1],data[0]))
			print("jobs in buffer %d"%jobs_in_buffer)
			print("MAX_JOBS == %d"%MAX_JOBS)
		elif MAX_JOBS == 0:
			print("Im done consuming")
			break
			# self.yield()
			# print("sleeping")
			# condition.wait()
			# print("awaken")
		else:
			print("imma block my self")
		# 	semaphore.acquire()
		# 	print("Unblocked")
	print("exit consumer")

	print(mobilejobs)
# socketcreate(sys.argv[1], int(sys.argv[2]))	



def main():

	global buff
	buff = [] # for both
	global mobilejobs
	mobilejobs = {} # for producer
	global jobs_in_buffer
	jobs_in_buffer = 0
	# index = 0
	global MAX_JOBS
	MAX_JOBS = 20
	global lock
	lock = Lock()

	global semaphore
	semaphore = Semaphore()
	semaphore.acquire() 	# start with consumer blocked
	
	# Create one threads to send jobs
	# Number of thread not needed but will be equal to mobile ID	

	producer = Thread(target = jobcreate, args=(sys.argv[1], int(sys.argv[2])))
	producer.start()

	consumer = Thread(target = consumejob)
	consumer.start()

	consumer.join()
	producer.join()
	
	

	# No se esta blockeando cuando termina proceso y no hay work


if __name__ == "__main__":
    main()	


