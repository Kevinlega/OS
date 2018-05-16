#!/usr/bin/env python
import sys

class VirtualMemoryAccess:
	def __init__(self): # Initialize list 
		
		self.list = []		#declare variables

		with open(sys.argv[2],"r") as file: # opens file and closes automatically at end
			instructions = file.read()		# read the file

		self.list = instructions.split()	# splits the input in the spaces

		for x in range(len(self.list)):
			self.list[x] = tuple(self.list[x].split(":"))

	def pop(self):		# Removes instruction done
		self.list.pop(0)

	def isEmpty(self):	# Returns True if list empty
		return self.list == []


class Pages():

	def __init__(self):
		self.length = 0
		self.list = []
		self.page_fault = 0			

	def addpage(self,page):								# Add page to list
		self.list.append(page)
		self.page_fault +=1	
		self.length +=1				

	def remove(self,position):							# Removes a page from the list 
		self.length -=1
		return self.list.pop(position)					

	def isFull(self):									# Returns True if list full
		return int(sys.argv[1]) == self.length		

	def getPageFault(self):								# Gives the page faults
		return self.page_fault		

	def index(self,page):								# Gives the first index occurence of page
		try:
			return self.list.index(page)
		except:
			return -1



def optimal(instruction, page):
	pages = page.list
	farthest_used = []
	for x in range(len(instruction)):
		farthest_used.append(instruction[x][1])

	# Case 1: if item in pages, but won't be used anymore
	for item in pages:
		if item in farthest_used:
			pass
		else:
			return pages.index(item)

	intersection = set(farthest_used)
	# Case 2: if item in pages, but won't be needed for a long time
	intersection = list(intersection.intersection(pages))

	orderRemove = []
	# print(farthest_used)

	# Remove every number in intersection not in farthest_used
	for x in range(len(farthest_used)):
		if farthest_used[x] in intersection:
			orderRemove.append(farthest_used[x])
		else:
			pass

	# for x in range(len(farthest_used)-1):
	while len(orderRemove) > 1:
		if orderRemove[0] == orderRemove[1]:
			# print(orderRemove)
			orderRemove.pop(0)
		else:
			# remove every encounter of item in z position
			# print(orderRemove)
			orderRemove = [item for item in orderRemove if item != orderRemove[0]]
			# print(orderRemove)
		
		# print(farthest_used)
	return pages.index(orderRemove[0])


# Check command line input, if wrong gives help on how to use
if len(sys.argv) !=3:
	sys.exit("Usage: python optimal.py <Number of physical memory pages> <access sequence file>")


instructions = VirtualMemoryAccess()
pages = Pages()


def main():
	global instructions,pages

	while not instructions.isEmpty():
		# maybe switch order of if and else
		# when it's empty
		if not pages.isFull() and pages.index(instructions.list[0][1]) == -1:
			pages.addpage(instructions.list[0][1])
			print(pages.list)
			instructions.pop()
		elif pages.index(instructions.list[0][1]) != -1:
			print(pages.list)
			instructions.pop()
			pass

		# when it's full and not in pages
		else:
			removing_page = optimal(instructions.list,pages)
			pages.remove(removing_page)
			pages.addpage(instructions.list[0][1])
			print(pages.list)
			instructions.pop()
			
	print("The number of page faults in the Optimal Replacement Algorithm is %d."%(pages.getPageFault()))

if __name__ == "__main__":								# To use main as main function
    main()	