# Homework 2: Threads and Scheduling by Kevin Legarreta 

## Program Description:

This project simulates a First Come First Served scheduling algorithm for a distributed system. It consists of mobile devices and a central computing server. It simulates a central server that receives requests for computing time from the mobile devices. It puts the jobs in a queue of processes, and then executes the jobs. Jobs are in the format "mobile_id:CPU_time". In the server, we have two threads, one that receives the jobs and writes them in the queue and the other reads from the queue and sleeps for the amount of time that it is stipulated in the job. Jobs arrive to the server via a socket UDP connection. The server binds itself to the port given by the user and the host localhost. We also have the mobile device which is an endless loop which connects to the server and keeps sending messages to the port and host given by the user. It generates a random integer to send as seconds to be consumed in the central computing server. The only way mobile stops is when a keyboard interrupt occurs from the user.

The program uses the libraries: 

- sys: For the parsing of the input.
- socket: For the socket creation.
- randint function from random: To get a random integer.
- threading: For the creation of threads, locks(mutexes), and semaphores.
- time: to use function sleep.	


## How to run program:

Must use python3 to run both scheduler and mobile. 

To run the server do:
```
python3 scheduler.py server_port
```
Where server port is the same for mobile and scheduler

To run the mobile do:
```
python3 mobile.py mobile_id host port
```

Where mobile_id must be different in each mobile, because if it's the same number they will be added like if the job was only from one mobile. Host must be set to localhost, because server is set to listen in localhost. Port must be set to the same value as in scheduler, meaning server_port = port.

For the connection to work only run server once and mobile one or more times.

##Contributors

The project was done by me, myself and I. Didn't contact other students to do the project, but students did contact me and I helped them on guiding them in the right correction. Doing so since I had most of the project done we discussed the common errors that I encountered. I don't know if that counts as helping and if they will add me to their README.md. Just in case I talked to Jose, Christian, and Emmanuel Nieves

Links I used to help me do the project:

- https://docs.python.org/3.1/library/random.html
- https://docs.python.org/3/library/functions.html#func-bytes
- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/2/library/string.html
- https://pymotw.com/2/socket/udp.html

For README.md templates used:

- https://gist.github.com/jxson/1784669 
- https://gist.github.com/PurpleBooth/109311bb0361f32d87a2
