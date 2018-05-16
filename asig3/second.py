#!/usr/bin/env python
import sys

class VirtualMemoryAccess:
	def __init__(self): # Initialize list 
		
		self.list = []		#declare variables

		with open(sys.argv[2],"r") as file: # opens file and closes automatically at end
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

	def index(self,instruction):		# Gives the first index occurence of page or -1 if not in
		try:
			return self.list.index(instruction)
		except:
			return -1

class pageTable():

	def __init__(self):
		self.length = 0			# length of FIFO 
		self.list = []			# basically a queue with replacement of last used to the last position
		self.page_fault = 0		# keeps track of page fault

	def addpage(self,page):								# Add page to list
		self.list.append(page)
		self.page_fault +=1			# increment page fault 
		self.length +=1			

	def remove(self,position=0):						# Removes a page from the list 
		self.length -=1
		return self.list.pop(position)					

	def isFull(self):									# Returns True if list full
		global pages_length
		return pages_length == self.length		

	def getPageFault(self):								# Gives the page faults
		return self.page_fault		

	def index(self,page):								# Gives the first index occurence of page
		try:
			return self.list.index(page)
		except:
			return -1

	def swap(self,page_position):					# move a page to the end if page hit
		x = self.list.pop(page_position)
		self.list.append(x)

def main():
	global instructions,pages


	while not instructions.isEmpty():	# continue until instructions end
		
		page_location =  pages.index(instructions.list[0])

		# when not full and page not in table
		if not pages.isFull() and page_location == -1:
			pages.addpage(instructions.list[0])
			instructions.pop()

		# when page hit	
		elif page_location != -1:
			if page_location != len(pages.list)-1:
				pages.swap(page_location)
			instructions.pop()

		# when it's full and not in pages
		else:
			pages.remove(0)
			pages.addpage(instructions.list[0])
			instructions.pop()
			
	print("The number of page faults in the Second Chance Algorithm is %d."%(pages.getPageFault()))


# Check command line input, if wrong gives help on how to use
if len(sys.argv) !=3:
	sys.exit("Usage: python second.py <Number of physical memory pages> <access sequence file>")


instructions = VirtualMemoryAccess()	#get instructions
pages = pageTable()						# init page table
try:
	pages_length = int(sys.argv[1])		# get page table size
except:
	sys.exit("Number of physical memory pages must be an integer or any number able to be converted to integer")


if __name__ == "__main__":								# To use main as main function
    main()	