#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#================================================================================
#DB NIOS4 (MYSQL VERSION)
#================================================================================
#standard class
import mysql.connector
from mysql.connector import Error
import os
import sys
import datetime
import random, string
import uuid
#================================================================================
#nios4 class
from utility_nios4 import utility_n4
from utility_nios4 import error_n4
#================================================================================
class database_nios4:

    def __init__(self,username,password,dbname,hostdb,usernamedb,passworddb):
        #controllo se esiste il database oppure no
        self.__host = hostdb
        self.__usernamedb = usernamedb
        self.__passworddb = passworddb
        self.__username = username
        self.__password = password
        self.__dbname = dbname
        self.viewmessage = True
        self.connectiondb = None

        #controllo se esiste il database se non esiste lo devo creare
        try:
            # Connessione al database MySQL
            connection = mysql.connector.connect(
                host=hostdb,  # Ad esempio, 'localhost' o l'IP del tuo server MySQL
                user=usernamedb,  # Il tuo username MySQL
                password=passworddb  # La tua password MySQL
            )

            if connection.is_connected():
                cursor = connection.cursor()
                # Verifica l'esistenza del database
                cursor.execute("SHOW DATABASES")
                databases = [db[0] for db in cursor]
                if dbname in databases:
                    print(f"Il database '{dbname}' esiste già.")
                else:
                    # Crea il database se non esiste
                    cursor.execute(f"CREATE DATABASE {dbname} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    print(f"Database '{dbname}' creato con successo.")

                self.initializedb()

        except Error as e:
            print(f"Errore durante la connessione al MySQL: {e}")
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("Connessione al MySQL chiusa.")

        self.err = error_n4("","")

    def exists_table(self,tablename):
        self.connectiondb = self.connectdb()
        cursor = self.connectiondb.cursor()
        query = f"SHOW TABLES LIKE '{tablename}'"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result is not None        

    def exists_field(self,tablename,fieldname):
        self.connectiondb = self.connectdb()
        cursor = self.connectiondb.cursor()
        query = f"SHOW COLUMNS FROM {tablename} LIKE '{fieldname}'"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result is not None  

    def connectdb(self):
        #connection on db
        #try:

        #if self.connectiondb == None:
        db_config = {
            'host': self.__host,    # L'indirizzo del server MySQL, può essere un indirizzo IP o un nome di dominio
            'user': self.__usernamedb, # Il tuo username MySQL
            'password': self.__passworddb, # La tua password MySQL
            'database': self.__dbname # Il nome del database a cui vuoi connetterti
        }
        self.connectiondb = mysql.connector.connect(**db_config)

        #if self.connectiondb.is_connected():            
        #    print("Connesso")
        #else:    
        #    db_config = {
        #        'host': self.__host,    # L'indirizzo del server MySQL, può essere un indirizzo IP o un nome di dominio
        #        'user': self.__username, # Il tuo username MySQL
        #        'password': self.__password, # La tua password MySQL
        #        'database': self.__dbname # Il nome del database a cui vuoi connetterti
        #    }
        #    self.connectiondb = mysql.connector.connect(**db_config)

        return self.connectiondb
        
        #except Exception as e:
        #    self.err.errorcode = "E001"
        #    self.err.errormessage = str(e)
        #    return None

    def stime(self):
        #return string of current date
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def initializedb(self):
        #inizialize db
        #if db non exist the class create file and create all standard tables of Nios4 for correct work
        try:
            #self.connectiondb = self.connectdb()

            if self.viewmessage == True:
                print("--------------------------------------------------------------------")
                print(self.stime() +  "     CREATE/CHECK DB")
                print("--------------------------------------------------------------------")
            

            if not self.exists_table("so_tables"):
                if self.viewmessage == True:
                    print(self.stime() +  "     create so_tables")
                if self.setsql("CREATE TABLE so_tables (gguid VARCHAR(40) Not NULL Default '' PRIMARY KEY, tid DOUBLE NOT NULL DEFAULT 0,eli INTEGER NOT NULL DEFAULT 0,arc INTEGER NOT NULL DEFAULT 0,ut VARCHAR(255) NOT NULL DEFAULT '' , displayable DOUBLE NOT NULL DEFAULT 0,eliminable DOUBLE NOT NULL DEFAULT 0,editable DOUBLE NOT NULL DEFAULT 0 , tablename TEXT,syncyes DOUBLE NOT NULL DEFAULT 0,syncsel DOUBLE NOT NULL DEFAULT 0,param TEXT NOT NULL,expressions TEXT NOT NULL,tablelabel TEXT NOT NULL,newlabel TEXT NOT NULL, ind INTEGER NOT NULL DEFAULT 0,lgroup TEXT NOT NULL)") == False:
                    return False

            if not self.exists_table("so_fields"):
                if self.viewmessage == True:
                    print(self.stime() +  "     create so_fields")
                if self.setsql("CREATE TABLE so_fields(gguid VARCHAR(40) NOT NULL DEFAULT '' PRIMARY KEY, tid DOUBLE NOT NULL DEFAULT 0,eli INTEGER NOT NULL DEFAULT 0,arc INTEGER NOT NULL DEFAULT 0,ut VARCHAR(255) NOT NULL, displayable DOUBLE NOT NULL DEFAULT 0,eliminable DOUBLE NOT NULL DEFAULT 0,editable DOUBLE NOT NULL DEFAULT 0 , tablename TEXT NOT NULL, fieldname TEXT NOT NULL, fieldlabel TEXT NOT NULL, fieldtype INTEGER NOT NULL DEFAULT 0, viewcolumn INTEGER NOT NULL DEFAULT 0, columnwidth DOUBLE NOT NULL DEFAULT 0, obligatory INTEGER NOT NULL DEFAULT 0, param TEXT NOT NULL, ofsystem INTEGER NOT NULL DEFAULT 0, expression TEXT NOT NULL, style TEXT NOT NULL, panel TEXT NOT NULL, panelindex INTEGER NOT NULL DEFAULT 0, fieldlabel2 TEXT NOT NULL, ind INTEGER NOT NULL DEFAULT 0, columnindex INTEGER NOT NULL DEFAULT 0)") == False:
                    return False

            if not self.exists_table("so_users"):
                if self.viewmessage == True:
                    print(self.stime() +  "     create so_users")
                if self.setsql("CREATE TABLE so_users(gguid VARCHAR(40) NOT NULL DEFAULT '' PRIMARY KEY, tid DOUBLE NOT NULL DEFAULT 0,eli INTEGER NOT NULL DEFAULT 0,arc INTEGER NOT NULL DEFAULT 0,ut VARCHAR(255) NOT NULL DEFAULT '' , username TEXT NOT NULL, password_hash TEXT NOT NULL, param TEXT NOT NULL, categories DOUBLE NOT NULL DEFAULT 0,admin INTEGER NOT NULL DEFAULT 0,id INTEGER NOT NULL DEFAULT 0, ind INTEGER NOT NULL DEFAULT 0)") == False:
                    return False

            if not self.exists_table("lo_setting"):
                if self.viewmessage == True:
                    print(self.stime() +  "     create lo_setting")
                if self.setsql("CREATE TABLE lo_setting(gguid VARCHAR(40) NOT NULL DEFAULT '' PRIMARY KEY, tidsync DOUBLE NOT NULL DEFAULT 0)") == False:
                    return False
                if self.setsql("INSERT INTO lo_setting(gguid, tidsync) VALUES ('0',0)") == False:
                    return False

            if not self.exists_table("lo_cleanbox"):
                if self.viewmessage == True:
                    print(self.stime() +  "     create lo_cleanbox")
                if self.setsql("CREATE TABLE lo_cleanbox(gguid VARCHAR(40) NOT NULL DEFAULT '' PRIMARY KEY, tid DOUBLE NOT NULL DEFAULT 0,tablename TEXT NOT NULL,gguidrif CHAR(40) NOT NULL DEFAULT '')") == False:
                    return False

            if not self.exists_table("lo_syncbox"):
                if self.viewmessage == True:
                    print(self.stime() +  "     create lo_syncbox")
                if self.setsql("CREATE TABLE lo_syncbox(gguid VARCHAR(40) NOT NULL DEFAULT '' PRIMARY KEY, tid DOUBLE NOT NULL DEFAULT 0,tablename TEXT NOT NULL,gguidrif CHAR(40) NOT NULL DEFAULT '')") == False:
                    return False

        except Exception as e:
            self.err.errorcode = "E002"
            self.err.errormessage = str(e)
            return False 

        return True

    def get_ind(self,tablename):
        #recupero l'indice da utilizzare per un nuovo record
        try:
            records=self.getsql(f"SELECT ind FROM {tablename} ORDER BY ind desc limit 1")
            if records:
                return records[0][0] + 1
            else:
                return 1
        except Exception as e:
            self.err.errorcode = "E006"
            self.err.errormessage = str(e)
            return 0   

    def convap(self,value):
        if value == None:
            return ""
        valore =str(value).replace("'", "''")
        return valore

    def addsyncbox(self,tablename,gguidrif):
        #aggiungo un record alla syncbox da inviare
        gguid = uuid.uuid4()
        tid = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

        stringa = f"INSERT INTO lo_syncbox (gguid,tid,tablename,gguidrif) "    
        stringa2 = f"VALUES ('{gguid}',{tid},'{self.convap(tablename)}','{gguidrif}')"

        return self.setsql(stringa + stringa2)

    def addcleanbox(self,tablename,gguidrif):
        #aggiungo un record alla cleanbox da inviare
        gguid = uuid.uuid4()
        tid = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

        stringa = f"INSERT INTO lo_cleanbox (gguid,tid,tablename,gguidrif) "    
        stringa2 = f"VALUES ('{gguid}',{tid},'{self.convap(tablename)}','{gguidrif}')"

        #cancello il valore se presente nella syncbox
        self.setsql(f"DELETE FROM lo_syncbox WHERE tablename='{self.convap(tablename)}' and gguidrif='{gguidrif}'")

        return self.setsql(stringa + stringa2)

    def setsql(self,sql):
        #Executes an sql command directly on the database passed with the conn parameter#set value
        try:
            self.connectiondb = self.connectdb()
            c = self.connectiondb.cursor()
            c.execute(sql)
            self.connectiondb.commit()
            c.close()
            self.connectiondb.close()
            return True
        except Exception as e:
            self.err.errorcode = "E004"
            self.err.errormessage = str(e)
            print("ERROR SQL ->" + str(e))
            return False

    def getsql(self,sql):
        #Retrieve a datatable with sql string on the standard database
        #try:
        self.connectiondb = self.connectdb()
        c = self.connectiondb.cursor()
        c.execute(sql)
        records = c.fetchall()
        c.close()
        self.connectiondb.close()
        return records
        #except Exception as e:
        #    self.err.errorcode = "E005"
        #    self.err.errormessage = str(e)
        #    return None

    def get_tablesname(self):
        #Retrieves all the names of the tables managed by Nios4
        try:
            records=self.getsql("SELECT tablename,tid FROM so_tables ORDER BY tablename")
            if records == None:
                return None
            tables = {}
            for r in records:
                tables[r[0]] = r[1]

            return tables
        
        except Exception as e:
            self.err.errorcode = "E006"
            self.err.errormessage = str(e)
            return None            

    def get_fieldstype(self,tablename):
        #Retrieves the type of fields from a specific table
        try:
            #records=self.getsql('PRAGMA TABLE_INFO({})'.format(tablename))
            records=self.getsql(f"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{tablename}' and TABLE_SCHEMA ='{self.__dbname}'")
            if records == None:
                return None
            tfields = {}
            for r in records:
                t = r[1]
                tfields[r[0]] = t

            return tfields

        except Exception as e:
            self.err.errorcode = "E007"
            self.err.errormessage = str(e)
            return None            

    def newrow(self,tablename,gguid):
        #Create a new row within the passed table with a gguid (id) set
        try:
            #list of skipped field
            skipfields = ["gguid"]
            
            s1 = "INSERT INTO " + tablename + "(gguid,"
            s2 = ") VALUES ('" + gguid + "',"

            tfields = self.get_fieldstype(tablename)
            for c in tfields:
                if c not in skipfields:
                    s1 = s1 + c + ","
                    if "varchar" in tfields[c]:
                        s2 = s2 + "'',"
                    elif tfields[c] == "BIGINT":
                        s2 = s2 + "0,"
                    elif tfields[c] == "int":
                        s2 = s2 + "0,"
                    elif tfields[c] == "integer":
                        s2 = s2 + "0,"
                    elif tfields[c] == "datetime":
                        s2 = s2 + "NULL,"
                    elif tfields[c] == "FLOAT":
                        s2 = s2 + "0,"
                    elif tfields[c] == "text":
                        s2 = s2 + "'',"
                    elif tfields[c] == "mediumtext":
                        s2 = s2 + "'',"
                    elif tfields[c] == "double":
                        s2 = s2 + "0,"

            sql=s1[:-1] + s2[:-1] + ")"

            if self.setsql(sql) == False:
                return False

            return True

        except Exception as e:
            print(str(e))
            self.err.errorcode = "E008"
            self.err.errormessage = str(e)
            return False            

    def get_fieldsname(self):
        #retrieves all currently created fields and tables
        #try:
        records=self.getsql("SELECT tablename,fieldname,tid,fieldtype FROM so_fields ORDER BY tablename")
        if records == None:
            return None
        fields = {}
        for r in records:
            key = str(r[0]).lower() + "|" + str(r[1]).lower()
            if key not in fields:
                fields[key] = [r[2],r[3]]

        #add fields
        records=self.getsql("SELECT tablename FROM so_tables ORDER BY tablename")
        if records == None:
            return None

        for r in records:
            tfields = self.get_fieldstype(r[0])
            for c in tfields:
                key = str(r[0]).lower() + "|" + str(c).lower()
                if key not in fields:
                    v = key.split("|")
                    if v[1] == "gguid" or v[1] == "ut" or v[1] == "uta" or v[1] == "exp" or v[1] == "gguidp" or v[1] == "tap" or v[1] == "dsp" or v[1] == "dsc" or v[1] == "utc":
                        fields[key] = [0,0]
                    elif v[1] == "tidc" or v[1] == "tid" or v[1] == "eli" or v[1] == "arc" or v[1] == "ind" or v[1] == "dsq1" or v[1] == "dsq2":
                        fields[key] = [0,10]
                    else:
                        if "varchar" in tfields[c]  or tfields[c] == "text" or tfields[c] == "mediumtext":
                            fields[key] = [0,0]
                        elif tfields[c] == "int" or tfields[c] == "integer" or tfields[c] == "DECIMAL" or tfields[c] == "FLOAT" or tfields[c] == "double":
                            fields[key] = [0,10]
                        else:
                            fields[key] = [0,0]

        return fields
        
        #except Exception as e:
        #    self.err.errorcode = "E010"
        #    self.err.errormessage = str(e)
        #    return None    


    def get_columnsname(self,tablename):
        #Retrieves the column names of a table
        #try:
        self.connectiondb = self.connectdb()
        c = self.connectiondb.cursor()
        c.execute("select * from " + tablename)
        return [member[0] for member in c.description]

        #except Exception as e:
        #    self.err.errorcode = "E011"
        #    self.err.errormessage = str(e)
        #    return None

    def get_gguid(self,tablename):
        #Get all gguids from a table
        try:
            values = []
            records=self.getsql("SELECT gguid,tid FROM " + tablename)
            if records == None:
                return None        
            values = {}
            for r in records:
                if r[0] not in values:
                    values[r[0]] = r[1]
            return values

        except Exception as e:
            self.err.errorcode = "E012"
            self.err.errormessage = str(e)
            return None



    def extract_sotables(self,tablename,TID):
        #It extracts the data of the tables that have been modified after a certain tid for sending to the synchronizer
        #try:
        values = []
        records=self.getsql("SELECT * FROM " + tablename + " where tid >= " + str(TID) + " ORDER BY ind")
        if records == None:
            return None

        columns_name = self.get_columnsname(tablename)
        if columns_name == None:
            return None
        
        for r in records:
            o = {}
            count =0
            for c in columns_name:
                o[c] = r[count]
                count =count+1
                
            values.append(o)

        return values

        #except Exception as e:
        #    self.err.errorcode = "E013"
        #    self.err.errormessage = str(e)
        #    return None

