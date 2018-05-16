#
#Lab 1: Simple thread creation laboratory excersise.
#Instructor: Jose R. Ortiz Ubarri

# Description: This code creates a number of threads that only counts numbers.
# The objective is to provide the student with:
#    - an easy to use Threads library
#    - to have a feel of concurrent programming
#    - generate a discussion on time sharing and scheduling
#    - and process priority
#

from threading import Thread

MAX_COUNT = 10

# Class to implement a python Thread.  Inheit all the functions from Thread

class CounterThread(Thread):
	
	# The constructor assign the internal id to the new thread.
	def __init__ (self, t_number):
			
		# This variable is used to assign an internal id to the thread.
		self.t_number = t_number
		Thread.__init__(self)

	# Define inside what the thread is to do.
	def run(self):
		# This thread counts the numbers from 0 to MAX_COUNT - 1
		# Something is missing here

			for i in range(MAX_COUNT):
				print(self.t_number, i)
		

			print("Thread %s finished" % self.t_number)

	

# Python main funtion.  Not necessary but to keep your C++ legacy...
def main():
	
	# In kernel threads you would like to set this variable
 	# to the number of cores in the system.
	idealThreads = 2

	thread = [0] * idealThreads

	# Create and start the threads
	for i in range(idealThreads):
		thread[i] = CounterThread(i)

	# Something is missing here.
	for i in range(idealThreads):
		thread[i].start()

	# Make the original thread wait for the created threads.
	for i in range(idealThreads):
		thread[i].join()


	# Something is missing here

	

if __name__ == "__main__":
    main()	



