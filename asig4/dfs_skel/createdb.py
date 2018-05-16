###############################################################################
#
# Filename: createdb.py
# Author: Jose R. Ortiz and Kevin Legarreta
#
# Description:
# 	Creates the database, added user and user check on other table like 
# 	Foreing keys.

import sqlite3
import getpass
import uuid
import hashlib

# Gets admin users information
name = input("Username to use: ")
while name == "":
	name = input("Try Again: ")
password = getpass.getpass(prompt="Password:  ")
while password == "":
	password = getpass.getpass(prompt="Try Again:")
salt = str(uuid.uuid4()).encode('utf-8')
password = password.encode('utf-8')

password = hashlib.md5( salt + password ).hexdigest()
password = str(password)

conn = sqlite3.connect("dfs.db") 

c = conn.cursor()

# Create a user table
c.execute("""CREATE TABLE users (uid INTEGER PRIMARY KEY ASC AUTOINCREMENT, name TEXT UNIQUE NOT NULL DEFAULT " ", hash TEXT NOT NULL DEFAULT " ", salt TEXT NOT NULL DEFAULT " ", admin INTEGER NOT NULL DEFAULT 0)""")

# Create inode table, don't know if the FOREIGN KEY works here just in case 
c.execute("""CREATE TABLE inode (fid INTEGER NOT NULL, owner INTEGER NOT NULL, fname TEXT NOT NULL DEFAULT " ", fsize INTEGER NOT NULL default "0", hash TEXT NOT NULL DEFAULT " ",  FOREING KEY owner REFERENCES users(uid),PRIMARY KEY (fname,owner))""")

# Create data node table
c.execute("""CREATE TABLE dnode(nid INTEGER PRIMARY KEY ASC AUTOINCREMENT, address TEXT NOT NULL default " ", port INTEGER NOT NULL DEFAULT "0")""") 

# Create UNIQUE tuple for data node
c.execute("""CREATE UNIQUE INDEX dnodeA ON dnode(address, port)""")

# Create block table 
c.execute("""CREATE TABLE block (bid INTEGER PRIMARY KEY ASC AUTOINCREMENT, fid INTEGER NOT NULL DEFAULT "0", nid INTEGER NOT NULL DEFAULT "0", cid TEXT NOT NULL DEFAULT "0",owner INTEGER NOT NULL,FOREING KEY owner REFERENCES users(uid))""")

# Create UNIQUE tuple for block
c.execute("""CREATE UNIQUE INDEX blocknc ON block(nid, cid,owner)""") 

# insert the admin user into the database
c.execute("""insert into users (name,hash,salt,admin) values ("%s", "%s", "%s",%d)""" % (name, password,salt,1))
# commits changes to the database
conn.commit()
# closes the connection to the database
conn.close()