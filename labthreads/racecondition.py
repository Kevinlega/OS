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

BUFFER_SIZE = 10000 # Maximum size of the Buffer

buffer_index = 0  # Shared index

mybuffer = [0] * BUFFER_SIZE # shared array to insert numbers.

# Class to implement a python Thread.  Inheit all the functions from Thread

class CounterThread(Thread):
	
	# The constructor assign the internal id to the new thread.
	def __init__ (self, t_number):
			
		# This variable is used to assign an internal id to the thread.
		self.t_number = t_number
		Thread.__init__(self)

	# Define inside what the thread is to do.
	def run(self):
		global buffer_index
		# Loop to insert numbers in the buffer
		while (buffer_index < BUFFER_SIZE):
			myIndex = buffer_index
			mybuffer[buffer_index] = myIndex
			buffer_index += 1
			

# Python main funtion.  Not necessary but to keep your C++ legacy...
def main():
	
	# In kernel threads you would like to set this variable
 	# to the number of cores in the system.
	idealThreads = 2

	thread = [0] * idealThreads

	# Create two threads to fill the buffer and start the threads	
	for i in range(idealThreads):
		thread[i] = CounterThread(i+1)
		thread[i].start()

	# Make the original thread wait for the created threads.

	for i in range(idealThreads):
		thread[i].join()

	# Display buffer content

	for i in range(BUFFER_SIZE):
		if mybuffer[i] != i:
			print "Buffer in position %s: %s" % (i, mybuffer[i])
	

if __name__ == "__main__":
    main()	



