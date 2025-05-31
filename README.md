## Introduction
This project was developed to work with Python 3 and is used to interact directly with the Nios4 data synchronizer.

The Nios4 cloud system is mainly based on two types of databases:

- The first database is the one that passes through the D-One synchronization server, where the data is formatted as json strings to be stored and exchanged between the various devices that require it. This allows you to have a database with identical tables that are not differentiated on the basis of the data they contain.

- The second database is the cloud one used by the web version, where the data are saved in their respective fields and tables to be used directly by the front-end.

The API of Nios4 [https://developer.nios4.com/web-api] they have been designed to read and write data directly from the web version database.

Instead, in this project we will use APIs that interact with data directly within the synchronization database.
The main difference is that while the APIs for the cloud normally manage one record at a time with the direct use of the synchronizer it is possible to manage many records simultaneously both reading and writing.

Another feature of the project is that the data is split (if necessary) into packages. That is, over a certain number of data (both read and write), the program will divide them into multiple packets to be sent and received to avoid overloading the network and possible data loss.

Currently, files and images are not managed. These will be managed in a future version of the project.

The project was tested on a Raspberry 3.

## Dependency
The only dependency that normally needs to be installed is the one for sqlite3 to manage the database. All the database management has been realized on an external class to allow to create a possible class connected to another type of database.

To install sqlite3 in linux environment (after giving the usual update and upgrade commands) type the following command from the terminal:

`sudo apt-get install sqlite3`

Or install python library for Linux and Windows:

`pip install db-sqlite3`

## Run the project
To run the project first you need a D-One account and a cloud database created by Nios4 (the free version is fine too)

- go to the site [https://web.nios4.com]
- register if you have not already done so and create a cloud database. The free version never expires.

Once this is done, open the test.py file and enter your account data and database name. This name is normally visible on the program. If you don't see it go to the site [https://www.d-one.store], log in with your details and enter the database management panel. The name you are interested in is written in parentheses next to the database title.

```sh
from sync_nios4 import sync_nios4

username = "username"
password = "password"
dbname = "numberdb"

sincro = sync_nios4(username,password)

valori = sincro.login()
if sincro.err.error == True:
    print("ERROR -> " + sincro.err.errormessage)

sincro.syncro(dbname)
if sincro.err.error == True:
    print("ERROR -> " + sincro.err.errormessage)
```

## Create data and synchronize it
Now that the database is present, it is possible to insert data into the tables. Remember that the tables so_ and lo_ are system, this means that you can still write and modify the data, but if you do not know their function you will create malfunctions on the programs.

The things to remember for a correct use of the program are:

- Always create records that do not contain `nil`. Within the database class there is a method to create a new record which can be used to avoid this `[db_nios4.newrow]` problem.

- To send data to the synchronizer, the value of the `tid` column must be changed. This column contains the time when the record was modified. At the end of each synchronization, the program saves the time of sending / receiving the data. At the next synchronization it will only check the records that have a time point greater than the one saved. Use the `[utility_nios4.tid]` function to retrieve the correct format of the tid value.
