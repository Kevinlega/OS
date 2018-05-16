###############################################################################
#
# Filename: test.py
# Author: Jose R. Ortiz and Kevin Legarreta
#
# Description:
#       Script to test the MySQL support library for the DFS project.
#
#

# This is how to import a local library
from mds_db import *
from Header import Login
# Create an object of type mds_db
db = mds_db("dfs.db") 

name = input("Userid if only one is 1: ")
while name == "":
	name = input("Try Again:")

name = int(name)

# Connect to the database
print("Connecting to database" )
db.Connect() 

# Testing how to add a new node to the metadata server.
# Note that I used a node name, the address and the port.
# Address and port are necessary for connection.

print("Choteando one of the steps of the assignment :) ...")
print("Files in the database")
for file, size in db.GetFiles(name):
	print("%s %s bytes"%(file, size))
print()

db.Close() 