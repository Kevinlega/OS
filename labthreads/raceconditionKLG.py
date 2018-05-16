# Kevin Legarreta 
# 801-14-3452
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
# Solution:
# To eliminate the race condition I eliminated the shared index,
# and implemented a divide and conquer algorithm. In this case 
# we have two threads and so what I did was give the first half
# to one thread and the other half to the other.
# 
# Running program:
# python2 raceconditionKLG.py
# for python3 change line 80 print to print("Buffer in position %s: %s" % (i, mybuffer[i]))


from threading import Thread

BUFFER_SIZE = 10 # Maximum size of the Buffer

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
		# Loop to insert numbers in the buffer  								# notice we do int(BUFFER_SIZE/2) just in case we get a real number 
		if self.t_number == 1:													# Task for the first thread 
			index = 0															# lists start at 0	
			while (index < int(BUFFER_SIZE/2)):									# only do if the half of the list is empty
				mybuffer[index] = index											# store the index in his index
				index += 1														# increment index
		else:																	# Task for second thread, since there is no other
			index2 = int(BUFFER_SIZE/2)											# start at half
			while (index2 >= int(BUFFER_SIZE/2) and index2 < BUFFER_SIZE):		# Start at half until buffer size -1 since it starts at 0 
				mybuffer[index2] = index2										# store the index in his index
				index2 += 1														# increment index
			

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
			print "Buffer in position %s: %s" % (i, mybuffer[i]) 	# python2
			# print("Buffer in position %s: %s" % (i, mybuffer[i])) python3

if __name__ == "__main__":
    main()	