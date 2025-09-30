#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#================================================================================
#DB NIOS4 (MYSQL VERSION)
#================================================================================
#standard class
from __future__ import annotations

import mysql.connector
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection  # precise connection type
from typing import Any, Dict, List, Optional, Tuple
import datetime
import uuid
#================================================================================
#nios4 class
from utility_nios4 import utility_n4
from utility_nios4 import error_n4
#================================================================================
class database_nios4:
    """
    Nios4 database helper for MySQL.

    This class initializes (and, if needed, creates) the target database and
    exposes a collection of convenience methods to introspect schema and run
    basic SQL operations used by Nios4.
    """
    def __init__(self,username:str,password:str,dbname:str,hostdb:str,usernamedb:str,passworddb:str) -> None:
        """
        Initialize the helper and ensure the database exists.

        Parameters
        ----------
        username : str
            Application-level username (stored by the class, not used by MySQL).
        password : str
            Application-level password (stored by the class, not used by MySQL).
        dbname : str
            Target MySQL database name.
        hostdb : str
            MySQL host (e.g., "localhost" or an IP/DNS).
        usernamedb : str
            MySQL user.
        passworddb : str
            MySQL password.

        Notes
        -----
        - Connects to the MySQL server (without selecting a DB),
          creates `dbname` if missing, then calls :meth:`initializedb`.
        - Any connection errors are printed and stored in `self.err`.
        """
        self.__host = hostdb
        self.__usernamedb = usernamedb
        self.__passworddb = passworddb
        self.__username = username
        self.__password = password
        self.__dbname = dbname
        self.viewmessage = True

        try:
            connection = mysql.connector.connect(
                host=hostdb,
                user=usernamedb,
                password=passworddb
            )

            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SHOW DATABASES")
                databases = [db[0] for db in cursor]
                if dbname in databases:
                    print(f"Il database '{dbname}' esiste già.")
                else:
                    cursor.execute(f"CREATE DATABASE {dbname} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    print(f"Database '{dbname}' created successfully.")

                self.initializedb()

        except Error as e:
            print(f"Error connecting to MySQL: {e}")
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()

        self.err = error_n4("","")
    #--------------------------------------------------------------------------------------
    def exists_table(self, tablename: str) -> bool:
        """
        Check whether a table exists.

        Parameters
        ----------
        tablename : str
            Table name to check.

        Returns
        -------
        bool
            ``True`` if the table exists, ``False`` otherwise.
        """        
        connectiondb = self.connectdb()
        cursor = connectiondb.cursor()
        query = f"SHOW TABLES LIKE '{tablename}'"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        connectiondb.close()
        return result is not None        
    #--------------------------------------------------------------------------------------
    def exists_field(self, tablename: str, fieldname: str) -> bool:
        """
        Check whether a field (column) exists in a table.

        Parameters
        ----------
        tablename : str
            Table name.
        fieldname : str
            Column name.

        Returns
        -------
        bool
            ``True`` if the column exists, ``False`` otherwise.
        """        
        connectiondb = self.connectdb()
        cursor = connectiondb.cursor()
        query = f"SHOW COLUMNS FROM {tablename} LIKE '{fieldname}'"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        connectiondb.close()
        return result is not None  
    #--------------------------------------------------------------------------------------
    def connectdb(self) -> Optional[MySQLConnection]:
        """
        Open a connection to the configured MySQL database.

        Returns
        -------
        Optional[mysql.connector.connection.MySQLConnection]
            A live MySQL connection if successful, otherwise ``None``.

        Notes
        -----
        Stores error details in ``self.err`` on failure.
        """
        try:

            db_config = {
                'host': self.__host,
                'user': self.__usernamedb,
                'password': self.__passworddb,
                'database': self.__dbname
            }
            connectiondb = mysql.connector.connect(**db_config)

            return connectiondb
        
        except Exception as e:
            self.err.errorcode = "E001"
            self.err.errormessage = str(e)
            return None
    #--------------------------------------------------------------------------------------
    def stime(self) -> str:
        """
        Get the current timestamp as a formatted string.

        Returns
        -------
        str
            Current timestamp formatted as ``'%Y-%m-%d %H:%M:%S'``.
        """
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #--------------------------------------------------------------------------------------
    def initializedb(self) -> bool:
        """
        Ensure core Nios4 tables exist; create them if missing.

        Returns
        -------
        bool
            ``True`` on success, ``False`` on failure.

        Notes
        -----
        Creates the following tables if absent:

        - ``so_tables``
        - ``so_fields``
        - ``so_users``
        - ``lo_setting`` (with an initial row)
        - ``lo_cleanbox``
        - ``lo_syncbox``
        """
        try:
            if self.viewmessage == True:
                print("--------------------------------------------------------------------")
                print(self.stime() +  "     CREATE/CHECK DB")
                print("--------------------------------------------------------------------")
            

            if not self.exists_table("so_tables"):
                if self.viewmessage == True:
                    print(self.stime() +  "     create so_tables")
                if self.setsql("CREATE TABLE so_tables (gguid VARCHAR(40) Not NULL Default '' PRIMARY KEY, tid DOUBLE NOT NULL DEFAULT 0,eli INTEGER NOT NULL DEFAULT 0,arc INTEGER NOT NULL DEFAULT 0,ut VARCHAR(255) NOT NULL DEFAULT '' , displayable DOUBLE NOT NULL DEFAULT 0,eliminable DOUBLE NOT NULL DEFAULT 0,editable DOUBLE NOT NULL DEFAULT 0 , tablename TEXT,syncyes DOUBLE NOT NULL DEFAULT 0,syncsel DOUBLE NOT NULL DEFAULT 0,param MEDIUMTEXT NOT NULL,expressions MEDIUMTEXT NOT NULL,tablelabel TEXT NOT NULL,newlabel TEXT NOT NULL, ind INTEGER NOT NULL DEFAULT 0,lgroup TEXT NOT NULL)") == False:
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
    #--------------------------------------------------------------------------------------
    def get_ind(self, tablename: str) -> int:
        """
        Compute the next `ind` value for a table.

        Parameters
        ----------
        tablename : str
            Table name.

        Returns
        -------
        int
            The next integer index (``max(ind)+1``), or ``0`` on error.
        """
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
    #--------------------------------------------------------------------------------------
    def convap(self, value: Optional[Any]) -> str:
        """
        Convert a Python value to a SQL-safe string for embedding in queries.

        Parameters
        ----------
        value : Any or None
            Value to convert.

        Returns
        -------
        str
            Empty string for ``None``; otherwise the string value with single
            quotes doubled (``'`` → ``''``).
        """
        if value == None:
            return ""
        valore =str(value).replace("'", "''")
        return valore
    #--------------------------------------------------------------------------------------
    def addsyncbox(self, tablename: str, gguidrif: str) -> bool:
        """
        Add a row to ``lo_syncbox`` (for outgoing sync).

        Parameters
        ----------
        tablename : str
            Table name to mark for sync.
        gguidrif : str
            Referenced row GUID.

        Returns
        -------
        bool
            ``True`` on success, ``False`` otherwise.
        """
        gguid = uuid.uuid4()
        tid = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

        stringa = f"INSERT INTO lo_syncbox (gguid,tid,tablename,gguidrif) "    
        stringa2 = f"VALUES ('{gguid}',{tid},'{self.convap(tablename)}','{gguidrif}')"

        return self.setsql(stringa + stringa2)
    #--------------------------------------------------------------------------------------
    def addcleanbox(self, tablename: str, gguidrif: str) -> bool:
        """
        Add a row to ``lo_cleanbox`` (to notify deletions/cleanup) and
        remove any matching entry from ``lo_syncbox``.

        Parameters
        ----------
        tablename : str
            Table name to mark for cleaning.
        gguidrif : str
            Referenced row GUID.

        Returns
        -------
        bool
            ``True`` on success, ``False`` otherwise.
        """
        gguid = uuid.uuid4()
        tid = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

        sql1 = f"INSERT INTO lo_cleanbox (gguid,tid,tablename,gguidrif) "    
        sql2 = f"VALUES ('{gguid}',{tid},'{self.convap(tablename)}','{gguidrif}')"

        # Remove from syncbox if present
        self.setsql(f"DELETE FROM lo_syncbox WHERE tablename='{self.convap(tablename)}' and gguidrif='{gguidrif}'")

        return self.setsql(sql1 + sql2)
    #--------------------------------------------------------------------------------------
    def setsql(self, sql: str) -> bool:
        """
        Execute a single SQL statement (no result expected).

        Parameters
        ----------
        sql : str
            SQL string to execute.

        Returns
        -------
        bool
            ``True`` on success, ``False`` otherwise.

        Notes
        -----
        Commits the transaction if the statement succeeds.
        """
        try:
            connectiondb = self.connectdb()
            if connectiondb is None:
                raise RuntimeError("Cannot open DB connection")            
            c = connectiondb.cursor()
            c.execute(sql)
            connectiondb.commit()
            c.close()
            connectiondb.close()
            return True
        except Exception as e:
            self.err.errorcode = "E004"
            self.err.errormessage = str(e)
            print("ERROR SQL ->" + str(e))
            return False
    #--------------------------------------------------------------------------------------
    def getsql(self, sql: str) -> Optional[List[Tuple[Any, ...]]]:
        """
        Execute a SQL query and fetch all rows.

        Parameters
        ----------
        sql : str
            SQL query to execute.

        Returns
        -------
        list of tuple or None
            A list of result rows (each row as a tuple) if successful;
            ``None`` on failure.
        """
        try:
            connectiondb = self.connectdb()
            if connectiondb is None:
                raise RuntimeError("Cannot open DB connection")            
            c = connectiondb.cursor()
            c.execute(sql)
            records: List[Tuple[Any, ...]] = c.fetchall()
            c.close()
            connectiondb.close()
            return records
        except Exception as e:
            self.err.errorcode = "E005"
            self.err.errormessage = str(e)
            return None
    #--------------------------------------------------------------------------------------    
    def get_tablesname(self) -> Optional[Dict[str, float]]:
        """
        Retrieve all Nios4-managed table names.

        Returns
        -------
        dict or None
            Mapping ``{tablename: tid}`` ordered by table name
            (as retrieved), or ``None`` on error.
        """
        try:
            records=self.getsql("SELECT tablename,tid FROM so_tables ORDER BY tablename")
            if records == None:
                return None
            tables: Dict[str, float] = {}
            for r in records:
                tables[str(r[0])] = r[1]

            return tables
        
        except Exception as e:
            self.err.errorcode = "E006"
            self.err.errormessage = str(e)
            return None            
    #--------------------------------------------------------------------------------------
    def get_fieldstype(self, tablename: str) -> Optional[Dict[str, str]]:
        """
        Retrieve the MySQL data type for each column of a table.

        Parameters
        ----------
        tablename : str
            Table name.

        Returns
        -------
        dict or None
            Mapping ``{column_name: data_type}`` (as reported by
            ``INFORMATION_SCHEMA.COLUMNS``), or ``None`` on error.
        """
        try:
            records=self.getsql(f"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{tablename}' and TABLE_SCHEMA ='{self.__dbname}'")
            if records == None:
                return None
            tfields: Dict[str, str] = {}
            for r in records:
                t = r[1]
                tfields[str(r[0])] = t

            return tfields

        except Exception as e:
            self.err.errorcode = "E007"
            self.err.errormessage = str(e)
            return None            
    #--------------------------------------------------------------------------------------
    def newrow(self, tablename: str, gguid: str) -> bool:
        """
        Insert a new row with the given GUID, auto-filling defaults.

        Parameters
        ----------
        tablename : str
            Target table.
        gguid : str
            GUID to assign to the ``gguid`` column.

        Returns
        -------
        bool
            ``True`` on success, ``False`` otherwise.

        Notes
        -----
        - Skips ``gguid`` when building the column list (it's inserted explicitly).
        - Assigns default values based on column data types detected via
          :meth:`get_fieldstype`.
        """
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
            self.err.errorcode = "E008"
            self.err.errormessage = str(e)
            return False            
    #--------------------------------------------------------------------------------------
    def get_fieldsname(self) -> Optional[Dict[str, Tuple[int, int]]]:
        """
        Retrieve all created fields and tables known to Nios4,
        enriched with currently present DB columns.

        Returns
        -------
        dict or None
            Mapping ``{ 'table|field': (tid, fieldtype) }``. If a field
            exists in the DB but not in ``so_fields``, a heuristic is used
            to infer ``fieldtype``. ``None`` on error.
        """
        try:
            records=self.getsql("SELECT tablename,fieldname,tid,fieldtype FROM so_fields ORDER BY tablename")
            if records == None:
                return None
            fields: Dict[str, Tuple[int, int]] = {}
            for r in records:
                key = str(r[0]).lower() + "|" + str(r[1]).lower()
                if key not in fields:
                    fields[key] = (int(r[2]), int(r[3]))

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
        
        except Exception as e:
            self.err.errorcode = "E010"
            self.err.errormessage = str(e)
            return None    
    #--------------------------------------------------------------------------------------
    def get_columnsname(self, tablename: str) -> Optional[List[str]]:
        """
        Retrieve the column names of a table.

        Parameters
        ----------
        tablename : str
            Table name.

        Returns
        -------
        list of str or None
            Column names in order, or ``None`` on error.
        """
        try:
            connectiondb = self.connectdb()
            if connectiondb is None:
                raise RuntimeError("Cannot open DB connection")            
            c = connectiondb.cursor()
            c.execute("select * from " + tablename)
            connectiondb.close()
            return [member[0] for member in c.description]

        except Exception as e:
            self.err.errorcode = "E011"
            self.err.errormessage = str(e)
            return None
    #--------------------------------------------------------------------------------------
    def get_gguid(self, tablename: str) -> Optional[Dict[str, float]]:
        """
        Get all GUIDs (`gguid`) with their `tid` from a table.

        Parameters
        ----------
        tablename : str
            Table name.

        Returns
        -------
        dict or None
            Mapping ``{gguid: tid}``, or ``None`` on error.
        """
        try:
            values = []
            records=self.getsql("SELECT gguid,tid FROM " + tablename)
            if records == None:
                return None        
            values: Dict[str, float] = {}
            for r in records:
                if r[0] not in values:
                    values[r[0]] = r[1]
            return values

        except Exception as e:
            self.err.errorcode = "E012"
            self.err.errormessage = str(e)
            return None
    #--------------------------------------------------------------------------------------
    def extract_sotables(self, tablename: str, TID: float) -> Optional[List[Dict[str, Any]]]:
        """
        Extract rows changed after a given `tid`, ready for synchronization.

        Parameters
        ----------
        tablename : str
            Source table name.
        TID : float
            Lower bound (inclusive) on the `tid` column.

        Returns
        -------
        list of dict or None
            A list where each item is a dict ``{column: value}`` representing
            a row. ``None`` on error.
        """
        try:
            values: List[Dict[str, Any]] = []
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

        except Exception as e:
            self.err.errorcode = "E013"
            self.err.errormessage = str(e)
            return None

