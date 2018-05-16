#!/usr/bin/env python
import sys

class VirtualMemoryAccess:
	def __init__(self): # Initialize list 
		
		self.list = []		#declare variables

		with open(sys.argv[3],"r") as file: # opens file and closes automatically at end
			instructions = file.read()		# read the file

		self.list = instructions.split()	# splits the input in the spaces

		for x in range(len(self.list)):		# forget about R and W
			ins = self.list[x].split(":")
			if str(ins[0]) != "W" and ins[0] != "R":
				sys.exit('The access sequence file is not in the correct format.')
			try:
				self.list[x] = int(ins[1])
			except:
				sys.exit('The access sequence file is not in the correct format.')


	def pop(self):		# Removes instruction done
		self.list.pop(0)

	def isEmpty(self):	# Returns True if list empty
		return self.list == []

	def index(self,instruction):			# Gives the first index occurence of page or -1 if not there
		try:
			return self.list.index(instruction)
		except:
			return -1

class Page():								# Is the page information inside the page table
	def __init__(self, page, r, time):
		self.list = [page,r,time]		

	def setR(self,r):						# Changes the reference bit
		self.list[1] = r
	
	def getR(self):							# Returns the reference bit
		return self.list[1]
	
	def setTime(self,time):					# Changes the time
		self.list[2] = time

	def getTime(self):						# Returns the last access time
		return self.list[2]

	def getPage(self):						# Returns the page  number
		return self.list[0]

class pageTable():								# Page table that hold every page. Basically a linked list
	def __init__(self):
		self.length = 0						# Length of the page table
		self.list = []						# The link list
		self.page_fault = 0					# Keeps track of all the Page Faults
		self.clock = 0						# Logical clock that changes on every insert 
		self.pointer = 0					# The clock arm pointer
		
	def addpage(self,instruction):			# Add page to list
		global pages_length

		self.page_fault +=1					# when page added is page fault
		self.length +=1						# one more page in the table					

		page = Page(instruction,1,self.clock)	# Create the page entry From class Page

		self.list.insert(self.pointer,page)		# insert the list in the pointer position

		self.pointer = (self.pointer + 1) % pages_length	# move the pointer (clock arm) 

	def remove(self,position=0):						# Removes a page from the list 
		self.length -=1									# decrease arm
		return self.list.pop(position)					

	def isFull(self):									# Returns True if list full
		global pages_length
		return pages_length == self.length		

	def getPageFault(self):							# Gives the page faults
		return self.page_fault		


	def index(self,page):								# Gives the first index occurence of page or gives -1 if not in
		for x in range(self.length):
			if self.list[x].getPage() == page:
				return x
		return -1

	def PageHit(self,location):							# Every page hit set reference bit to 1 and change Last Access
		self.list[location].setTime(self.clock)
		self.list[location].setR(1)



def printpage():
	global pages
	string = '[ '
	for x in range(len(pages.list)):
		string += str(pages.list[x].list) + " "
		if x != len(pages.list)-1:
			string += ', '
	string += ']'
	print(string)


def main():
	global instructions,pages,tau,pages_length

	while not instructions.isEmpty():
		
		pages.clock +=1
		page_location =  pages.index(instructions.list[0]) # gets page location		
		
		# when it's not full and not in pages
		if not pages.isFull() and page_location == -1:	
			print("%s is a Page Fault at time %s."%(instructions.list[0],pages.clock))   
			pages.addpage(instructions.list[0])
			# print('Hand points: %s '%pages.pointer)
			# printpage()
			instructions.pop()

		# when page hit	
		elif page_location != -1:
			pages.PageHit(page_location)
			# printpage()
			instructions.pop()

		# when it's full and not in pages
		else:
			print("%s is a Page Fault at time %s."%(instructions.list[0],pages.clock))  
			small = [None,None] 		#Only for else, [0] holds pointer location and [1] holds smallest time
			found = False				

			for x in range(len(pages.list)* 2):
				if pages.list[pages.pointer].getR() == 1:  # change R to 0
					pages.list[pages.pointer].setR(0)
					pages.pointer = (pages.pointer + 1) % pages_length	# moves clock arm
					# printpage()

				else:
					if (pages.clock) - pages.list[pages.pointer].getTime() > tau:
					#removes page not in working set

						pages.remove(pages.pointer)
						pages.addpage(instructions.list[0])
						found = True
						# printpage()
						break
					else:
						try:		# needed because it starts in None and cant compare None with int
							if small[1] > pages.list[pages.pointer].getTime(): # Checks if record time is bigger to change it
								small = [pages.pointer,pages.list[pages.pointer].getTime()]
							pages.pointer = (pages.pointer + 1) % pages_length				# moves pointer foward
								
						except: # first case
							small = [pages.pointer,pages.list[pages.pointer].getTime()]
							pages.pointer = (pages.pointer + 1) % pages_length				# moves pointer foward
							

			if not found:		# case that remembers smallest time now removes

				pages.remove(small[0])
				# pages.pointer = small[0] # not moved to the removing page because cheo said so
				pages.addpage(instructions.list[0])
				# printpage()
			instructions.pop()	# go on to next instruction
			
	print("The number of page faults in the WSClock Page Replacement Algorithm (WSCRA) is %d."%(pages.getPageFault()))


# Check command line input, if wrong gives help on how to use
if len(sys.argv) !=4:
	sys.exit("Usage: python optimal.py <Number of physical memory pages> <tau> <access sequence file>")


instructions = VirtualMemoryAccess() #get instructions
pages = pageTable()	# init page table
try:
	pages_length = int(sys.argv[1])		# get page table size
	tau = int(sys.argv[2])				# get tau
except:
	sys.exit("Number of physical memory pages and tau must be an integer or any number able to be converted to integer")


if __name__ == "__main__":								# To use main as main function
    main()	