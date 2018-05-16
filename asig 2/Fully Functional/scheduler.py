# Kevin Legarreta				801-14-3452
import sys												# For argument parsing
import socket 											# For socket creation
from threading import Thread, Lock, Semaphore 			# Only bring Thread, Lock (mutex) and Semaphore 
import time												# To make thread sleep 

# Every commented print in threads run where use to try the scheduler. If want to uncommment must add lock.acquire and
# lock.release because the console is shared, which will be also part of the critical region.

# Implementation of class Queue with history, this class can store the data and keep track of how many jobs have been in
# the queue (it doesn't matter if it's not there no more, because it keeps the history):
class Queue:

	def __init__(self):									# Initialize queue variables

		self.queue = []									# Shared queue
		self.history = 0								# Used to keep track of how many items have been in queue
														# Basically another global variable, handle by class queue

	def enqueue(self,job):								# Add job to queue

		self.queue.append(job)							# Add job to queue(queue)
		self.history += 1

	def dequeue(self):									# Removes job to be done from queue

		return self.queue.pop(0)						# Removes and returns the next job to be done

	def isEmpty(self):
		return self.queue == []							# Returns True if queue empty

	# def Length(self):									# Not used, but can help if no isEmpty function
	# 	return len(self.queue)							# Return how many elements are in queue

	def queue_History(self): 							
		return self.history 							# Return how many elements have been in the queue



# Thread to produce jobs
class Producer(Thread):

	def __init__(self):									# Initialize Producer thread
		Thread.__init__(self)							# By calling the init function in Thread

	def run(self): 										# Job to do

		# print("UDP socket up and running listening")	# To know when producer up, but needs lock.acquire and release
		s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)	# Creates a UDP socket named s
		s.bind(connection)								# Binds socket to localhost and the port number					

		while True:
			lock.acquire()

			localhistory = q.queue_History() 		# Just in case the "if" fails we check if queue has reached 
													# maximum jobs in queues

			lock.release()							# so we use mutex to get a local copy 

			if localhistory != MAX_JOBS:			# Keep running until no more jobs can me put in queue

				data, addr = s.recvfrom(1024)				# Get the message from mobile in data and address of mobile in 
															# addr
				lock.acquire()	 							# Lock the critical region with the mutex

				q.enqueue(data)								# Add data to the queue, critical region because is shared
	
				lock.release()								# Unlock the mutex
				try:
					semaphore.release()						# Unlock the consumer
				except:
					continue

				if q.queue_History() == MAX_JOBS:
					break
		s.close()										# Close socket connection
		# print("UDP server done")						# To know when producer died, but needs lock.acquire and release

# Thread to consume jobs
class Consumer(Thread):

	def __init__(self):									# Initialize Consumer thread
		Thread.__init__(self)							# By calling the init function in Thread

	def run(self): 										# Job to do

		semaphore.acquire() 							# Make sure that the consumer starts locked
						
		while True:

				lock.acquire()							# mutex lock

				localempty = q.isEmpty()				# Since this is a global variable it may cause a raise condition
														# So we make it local
				localhistory = q.queue_History() 		# Just in case the "if" fails we check if queue has reached 
														# maximum jobs in queues

				lock.release()							# so we use mutex to get a local copy, mutex unlock

				if not localempty:						# If queue not empty means there is a job waiting						
					
					lock.acquire()						# mutex lock because we use shared queue
					data = q.dequeue()					# Pop the next element in queue and returns to data
					lock.release()						# mutex unlock			
					
					data = data.decode("utf-8")         # Convert back to string

					data = data.split(":")				# Split at ":" a list where index = 0 is mobile id and index 1 is 
														# job
					data[0] = int(data[0])				# Make mobile id integer
					if data[0] in mobilejobs:		# Checks if that mobile id is in dictionary
		 				mobilejobs[data[0]] += int(data[1])   # and add the previous time plus the 
													    # new request job
					else:								# Mobile id wasn't in the dictionary
						mobilejobs[data[0]] = int(data[1]) 	# Create the new item in dictionary equals to the time given

					# print("consuming")				# To know when consumer is consuming,but needs
														# lock.acquire and release
					time.sleep(int(data[1]))			# Do the job which is sleep for that amount of time
	
				elif localempty and (localhistory != MAX_JOBS): 
					# print("Blocking consumer")		# To know when consumer is blocked,but needs
														# lock.acquire and release
					semaphore.acquire()					# Block itslef because there is no job to be done

				elif MAX_JOBS == localhistory and localempty:
					# print("Im done consuming")		# To know when consumer is done,but needs
														# lock.acquire and release	
					break 								# Break out of endless loop because Nth job reached and 
														# all the jobs were executed			
						
		# print("exit consumer") 					# To know when consumer died, but needs lock.acquire and release

def main():
	
	global semaphore        							# state that it is the global semaphore
	semaphore.acquire() 								# start with consumer blocked

	producer = Producer()								# Listener to jobs
	consumer = Consumer()								# Executes jobs

	consumer.start()									# Start Consumer
	producer.start()									# Start Producer


	consumer.join()										# Make them wait for both threads to be done before exiting 
	producer.join()
	
	print("Both Producer and Consumer are done with their jobs.")
	print("The mobiles consumed:")

	keys = list(mobilejobs.keys())					# Gives a list of the keys in the dictionary
	keys.sort()										# Sorts keys of dictionary

	for x in keys:									# Print all the jobs
		print("Mobile %s consumed %s seconds in CPU time"%(x,mobilejobs[x]))		


# Declare before main. Are here because they use Queue class and needs to be after Queue class implementation because 
# it's an interpreter

# global variables
q = Queue()												# To keep track of jobs sent by mobile !!! Shared
mobilejobs = {} 										# Consumer dictionary     !!! Not shared only used by consumer
MAX_JOBS = 15	   										# Nth job stop !!! Global not modified, only read; like C++ const
HOST = 'localhost'										# To set host to localhost always
PORT = int(sys.argv[1])									# To set port to system input and make int
connection = (HOST,PORT)								# Tuple that holds connection
semaphore = Semaphore()									# Make a Semaphore Object 
lock = Lock()											# Make a Mutex Lock 	  
	  
if __name__ == "__main__":								# To use main as main function
    main()	