#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#==========================================================
#TEST SYNC NIOS4
#==========================================================
from sync_nios4 import sync_nios4

#Enter your D-One account details
username = "username"
password = "password"

#test update github

#Enter the name of the cloud database
#If you don't know, go to d-one.store
#Log in with your data and go to the database management page
#Next to the database title in parentheses you will find the name
dbname = "dbname"

#We create the synchronizer object by giving it the username and password
sincro = sync_nios4(username,password)

#We require the login to the server, in this way we also check our data
values = sincro.login()
if sincro.err.error == True:
    print("ERROR -> " + sincro.err.errormessage)


#After logging in, we proceed to synchronize
#The first time the program will create the database and download the data
#Subsequent times it will send and receive only the new or modified data
sincro.syncro(dbname)
if sincro.err.error == True:
    print("ERROR -> " + sincro.err.errormessage)
