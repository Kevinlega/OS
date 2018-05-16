# Lab: Processes and Threads


University of Puerto Rico

Rio Piedras Campus

Dept. of Computer Science Introduction to Programming in C++

Instructor: José R. Ortiz-Ubarri email: jose.ortiz23@upr.edu

## Instructions
For this laboratory we will use the Threads libraries that can be found: [https://docs.python.org/2/library/threading.html](https://docs.python.org/2/library/threading.html)

The instructor will review the Library at the beginning of the laboratory.

The objectives are to provide the student with:

* an easy to use Threads library
* to have a feel of concurrent programming
* generate a discussion on time sharing and scheduling
* to have a simple experience that generates race conditions

## Part 1: Simple Threads

Modify the code in the file threadcreation.py by filling the lines with the message: 
```Some- thing is missing here. ```

The idea is for each thread to count until MAX\_COUNT displaying the thread\_id, the current count\_number.

1. Increase MAX_COUNT adding 0’s to the end of the number. 
￼￼
2. Modify the code such that each thread displays only a message with its id. Analyse the behaviour of the output.

## Part 2: Race conditions

1. Increase and decrease the BUFFER\_SIZE variable in file racecondition.py and analyze the results.

2. Fix such that there is no raceconditions among the threads created without using mutexes or semaphores, or any other synchronization support.

## Deliverables

Submit the solution to the part 2 `racecondition.py` in moodle.

