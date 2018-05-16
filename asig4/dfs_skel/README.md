# Assignment 04: Distributed File System by Kevin Legarreta 

## Program Description:
This project is a simple implementation of a file system, yet functional, distributed file system (DFS). The system contains inodes, data blocks, and users. Everything in done in the sistem the user must be logged in. The components in the DFS are:
 
#### The meta data server

The meta data server contains the metadata (inode) information of the files in your file system. It will also keep registry of the data servers that are connected to the DFS, and keep track of users registered. Functions as a inodes repository, log in the users, verifies admin privilege, removes files, removes users, lists the files of a user, list all the users, manages the copy request and removes the users

Your metadata server provides the following services:

1. Listen to the data nodes that are part of the DFS. Every time a new data node registers to the DFS the metadata server must keep the contact information of that data node. This is (IP Address, Listening Port). 
2. To ease the implementation the DFS the directory file system must contain four things: 
    - the path of the file in the file system
    - the nodes that contain the data blocks of the files
    - the file size
    - the hash of the file

2. Every time a client (commands list or copy) contacts the meta data server for:
    * requesting to read a file: the metadata server must check if the file is in the DFS database, and if it is, it return the nodes with its blocks_ids that contain the file.

    * requesting to write a file: the metadata server must:
        - insert in the database the path of the new file and name of the file, and its size. 
        - return a list of available data nodes where to write the chunks of the file
        - then store the data blocks that have the information of the data nodes and the block ids of the file.  

    * requesting to list files:
        - the metadata server must return a list with the files in the DFS and their size.

    * remove a file:
        - the metadata server must remove the file from database and return the OK message to the client.

    * remove a user:
        - the metadata server must remove the user and return the OK message to the client.

    * register a new user:
        - the metadata server must recieve a new user,salt, admin privilege, and password to insert a new user.

    * requesting to list users:
        - the metadata server must return a list with the usernames registered in the DFS. 

    * requesting to move a file:
        - the metadata server must update the filename including the path to the new provided name.
    * requesting to update password:
        - the metadata server must recieve a password hash it and update it on the users password column.

#### The data node server

The data node is the process that receives and saves the data blocks of the files or deletes the data blocks. It must first register with the metadata server as soon as it starts its execution. The data node receives the data from the clients when the client wants to write a file,returns the data when the client wants to read a file, and removes the data blocks on a remove request.

Your data node must provides the following services:

1. Listen to writes (puts):
    * The data node will receive blocks of data, store them using user and unique id concatenated, and return the unique id of the file of the user. We use concatenated id and user so that we can have same ids between different users.
    * Each node must have its own blocks storage path.  You may run more than one data node per system.
2. Listen to reads (gets):
    * The data node will receive request for data blocks, and it must read the data block, and return its content.
3. Listen to remove (remove):
    * The data node will recieve a remove request with the blockid and will compute the filename using the provided user and will call os.remove to remove the chunk of the file.

#### The list client

The list client just sends a list request for a user account to the meta data server and then waits for a list of file names with their size.

#### The copy client

It is in charge of copying the files from and to the DFS in the logged in user account.

The copy client:

1. After the user has successfully logged in it will continue to step 2 or 3.

2. Write files in the DFS
    * Log in the user and computes the hash of the file.
    * The client sends to the metadata server the file name, hash and size of the file to write.
    * Recieves the metadata server response with the list of available data nodes.
    * Send chunksized data blocks to each data node until covered the whole file in round robin.
    * Send the datablocks to the metadata to store them on the database.  

3. Read files from the DFS
    * Contact the metadata server with the file name to read.
    * Wait for the block list with the block id, hash and data server information
    * Retrieve the file blocks from the data servers.
    * Writes to a new file.
    * Compare the new file hash with the hash stored on the database.

#### The move client
The move client updates the path and name of a users file in the DFS.

#### The remove client
 The remove client will request the metadata the blocks of a users owned file, send a remove request for every block to the data node, after that we send a remove request to the metadata to remove the file from the database.

#### The remove users client for admins
The remove users client can only be executed by admins and it will be in charge of contacting the metadata and requesting the list of files of a user. After it has the list of files it will contact the metadata server to get every files data blocks location to send a remove request to the data nodes. When every data block of a file has been removed he will remove the user by contacting the metadata and requesting a remove user.

#### The list users client for admins
The list users client only runs with admin privilege to list every user on the metadata server.

#### The register user client for admins
The register user client is runned by and admin privilege and creates a new account with or without admin privilege and request the metadata server to register the user.

#### The update password client
The update password client is in charge of contacting the metadata server and change the logged in users password.

#### The header library
We have a header library that holds the helper functions used in almost all the files. 

- Login(address): which contacts the metadata server and checks if you're a user, and return the username. Recieves the tuple with the ip and address to the metadata server.

- Admin(ip,mport): which contacts the metadata server and check if you're admin. Recieves the metadata ip and port.

- encode(p): which encodes a given packet in the python3 dynamic

- recvall(sock,size): which is in charge of waiting until it recieved the full packet. Takes the socket that will recv the answer and the size of the expected packet.

- sendSize(sock,size): which is in charge of sending the size of a packet by the given socket.

- recieveSize(sock): which is in charge of recieving the size of packet.

- getChunkSize(fsize): which is in charge of deciding the chuncksize of data to use to cut a file given the file size of the file.

- ComputeHash(path): which is in charge of computing the md5 hash of a given file path to store it on the db or to compare to the one on the DFS.

#### The Packet Library Updates
The packet library was updated with some other functions to help with the other features:

- BuildPutChunk(chunksize,user): Sends the size of the chunk and the username of the person copying.

- getChunkSize(): returns the chunksize to be recieved

- BuildBlockSize(packet_size): Builds a put packet for data-node and sends the chunksize.

- getPacketSize(): Returns the chunksize in a packet.

- getHash(): Returns the hash of a file from the packet.

- BuildRemove(blockid,fname,user): Builds a remove file packet.

- BuildMove(fname,new_name,user): Builds a move file packet.

- RegisterUserPacket(user,password,salt,admin): Builds a register packet

- GetNewUserInfo(): Gets the info of a register new user packet.

- CheckAdmin(user,password): Builds a check admin packet.

-  Login(user,password): Builds a login packet.

- GetUserInfo(): Returns user and password of packet.

- ListUser(): Builds a list user packet.

- BuildListUserResponse(lusers): Builds a list user response packet. Not used but later on will be used. 

- UpdatePass( user,password): Builds a update password packet.

- GetUser(): Gets the user out of a packet.

-  RemoveUser(user): Builds a remove user packet.

#### The mds_db Library Updates
The mds_db library was updated with some other functions to help with the other features:

- RemoveFile(fname,user): Remove remove node list and file from database.

- MoveFile(fname,new_name,user): Moves file. Basically changes the name of the file.

- InsertUser(user, password,salt,admin):Inserts new user to the database. 

- GetSalt(user): Retrieves the salt of a given user to compute the password.

- Login(user,password): Basically checks if the password hashed matches to the uid give and return the uid so that we can decide send the ok of the login.
    
- CheckAdmin(user): Verifies the Admin priveledge of a given user.

- GetUsers(): Returns a list of users.    

- GetUserID(user): Retrives the user id given a username.  

- RemoveUser(user): Removes a user from the database.

## How to run program:

#### Creating an empty database:
The script createdb.py generates a database *dfs.db* for the project and inserts the first admin.

<pre>
    python3 createdb.py
</pre>


#### The meta data server
The metadata server must be run after creation like so:
<pre>
    python3 meta-data.py &lt;port, default=8000&gt;
</pre>

If no port is specified the port 8000 will be used by default.


#### Data Nodes:
Needs to have the metadata connection to run. To use the copy client, remove and remove users must have all registered data nodes running. To do so:
<pre>
    python3 data-node.py &lt;server address&gt; &lt;port&gt; &lt;data path&gt; &lt;metadata port,default=8000&gt;
</pre>

Server address is the meta data server address, port is the data-node port number, data path is a path to a directory to store the data blocks, and metadata port is the optional metadata port if it was ran in a different port other than the default port.

#### The copy client:

The copy client needs the metadata connection and the data nodes connection, must be run:

Copy from DFS:
<pre>
    python3 copy.py &lt;server&gt;:&lt;port&gt;:&lt;dfs file path&gt; &lt;destination file&gt;
</pre>

To DFS:
<pre>
    python3 copy.py &lt;source file&gt; &lt;server&gt;:&lt;port&gt;:&lt;dfs file path&gt;
</pre>

Where server is the metadata server IP address, and port is the metadata server port.
The dfs path must look like a normal path to a file. Example: /home/file.txt

#### The list client:

The list client needs the metadata connection, must be run:
<pre>
    python3 ls.py &lt;server&gt;:&lt;port, default=8000&gt;
</pre>

Where server is the metadata server IP and port is the metadata server port.  If the default port is not indicated the default port is 8000 and no ':' character is necessary.  

#### The move client
The move client needs the metadata connection and the data nodes connection, must be run:
<pre>
    python3 mv.py &lt;server&gt;:&lt;port&gt;:&lt;dfs file path&gt; &lt;new_filename&gt;
</pre>

Where server is the metadata server IP and port is the metadata server port.  If the default port is not indicated the default port is 8000 and no ':' character is necessary. DFS path is the file you want to move, and the new filename is the new file path going to be given.

#### The remove client
The remove client needs the metadata connection and the data nodes connection, must be run:
<pre>
    python3 mv.py &lt;server&gt;:&lt;port&gt;:&lt;dfs file path&gt; 
</pre>

Where server is the metadata server IP and port is the metadata server port. If the default port is not indicated the default port is 8000 and no ':' character is necessary. DFS path is the file you want to remove.

#### The remove users client for admins
The remove users client for admins needs the metadata connection and the data nodes connection, must be run:
<pre>
    python3 mv.py &lt;server&gt;:&lt;port&gt;:&lt;username to remove&gt; 
</pre>

Where server is the metadata server IP and port is the metadata server port.  If the default port is not indicated the default port is 8000 and no ':' character is necessary. And the username to remove is the user you want to remove.

#### The list users client for admins
The list user client for admins only needs the metadta connection, must be run:
<pre>
    python3 list_users.py &lt;server&gt;:&lt;port, default=8000&gt;
</pre>

Where server is the metadata server IP and port is the metadata server port.  If the default port is not indicated the default port is 8000 and no ':' character is necessary. 

#### The register user client for admins
The register user client for admins only needs the metadta connection, must be run:
<pre>
    python3 register.py &lt;server&gt;:&lt;port&gt; &lt;new_user&gt; &lt;admin=1:user=0&gt;
</pre>

Where server is the metadata server IP and port is the metadata server port.  If the default port is not indicated the default port is 8000 and no ':' character is necessary. new_user is the username of the new user and admin takes values of 1 and 0. 


#### The update password client
The update password client only needs the metadta connection,must be run:
<pre>
    python3 updatePass.py &lt;server&gt;:&lt;port, default=8000&gt;
</pre>

Where server is the metadata server IP and port is the metadata server port.  If the default port is not indicated the default port is 8000 and no ':' character is necessary. 

## Contributors 

Ian Manuel Dávila helped me explaining the structure of the DFS when I was lost on what was the DFS supposed to do. People contacted me for help, what I did was try to explain how it worked and send them a picture of how the metadata server, data nodes and the clients should look like. Other than that were the following links:

1. https://docs.python.org/2/library/socketserver.html
2. https://docs.python.org/2/library/uuid.html
3. https://docs.python.org/2/library/json.html
4. https://docs.python.org/2/library/sqlite3.html   
5. https://wiki.python.org/moin/Md5Passwords
6. https://pymotw.com/2/getpass/
7. https://docs.python.org/3.2/library/uuid.html?highlight=uuid
8. https://docs.python.org/3/library/hashlib.html
9. https://www.pythoncentral.io/hashing-files-with-python/


## Future Works

1. Update admin privilege on users.
2. Utilizar threads to write data blocks in the data nodes.
3. Create a Web client.
4. Every time the data node boots checks if every file in the data path are actually of the system, if not delete them
5. Encrypt the file chunks on the data node and send the client the key to decrypt it, so that the copy client send to store on the metadata server the data node and the key to decrypt the file chunk stored on that data path.
6. Create privilege flags like chmod chown and all that.
7. Send the chunks of data to the data nodes via a packet.
8. Maybe encrypt the packet before sending.