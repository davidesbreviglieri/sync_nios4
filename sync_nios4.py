#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#================================================================================
#Copyright of Davide Sbreviglieri 2024
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
#================================================================================
#SYNC NIOS4
#================================================================================
import os
import json
import sys
import uuid
import requests
import urllib.request
from datetime import datetime,timezone
from urllib.parse import quote
import uuid
#================================================================================
from utility_nios4 import error_n4
from utility_nios4 import utility_n4
from database_nios4 import database_nios4
#================================================================================

class sync_nios4:

    def __init__(self,username,password,token,dbname,hostdb,usernamedb,passworddb):
        #initialize class
        self.__username = username
        self.__password = password
        self.__token = token
        self.__dbname = dbname
        #standard path of db file
        #self.__db = database_nios4(os.path.abspath(os.getcwd()) + "/database") #initialize for sqlite
        self.__db = database_nios4(username,password,dbname,hostdb,usernamedb,passworddb)
        self.__utility = utility_n4
        #class for errors
        self.err = error_n4("","")
        self.__db.err = self.err
        #if view message log on console
        self.viewmessage = True
        self.__db.viewmessage = self.viewmessage
        #maximum number of lines that can be shipped at a time
        self.nrow_sync = 5000
        
        self.enabled_create_tables = [] #tabelle che devono essere create
        self.enabled_getdata_tables = [] #tabelle che devono essere create e ricevere i dati
        self.enabled_setdata_tables = [] #tabelle che devono essere create e inviare i dati

        if token == "":
            self.login()

    #----------------------------------------------------------------------------
    def send_notificationrecord(self,uta,title,description,tablename,gguidrif):
        #inserisco una notifica per l'apertura di una scheda
        #{"TAP":"rapportiintervento","GGUIDP":"4720979e-8590-43fe-b1b5-83f81a4c86bb"}
        di = {}
        di["TAP"] = tablename
        di["GGUIDP"] = gguidrif

        gguid = uuid.uuid4()
        tid = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        param = self.convap(json.dumps(di,ensure_ascii=False))
        data = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        stringa = f"INSERT INTO so_notifications (gguid,gguidp,tid,eli,arc,ut,uta,exp,ind,tap,dsp,dsc,dsq1,dsq2,utc,tidc,param,repeat_b,notificationdescription,tdescription,noticedate,remindertype,dateb,notificationsystem,date,read_b,notificationtype,notificationtitle,ttitle) "    
        stringa2 = f"VALUES ('{gguid}','',{tid},0,0,'nios4.clock','{uta}','',0,'','','',0,0,'nios4.clock',{tid},'{param}',0,'{self.convap(description)}','','{data}',0,'{data}','nios4','{data}',0,3,'{self.convap(title)}','')"

        self.setsql(stringa + stringa2)
        self.addsyncbox("so_notifications",gguid)
    #----------------------------------------------------------------------------
    def send_emailv2(self,dbname,sendfrom,sendfromname,sendto,subject,replyto,body,bodyhtml,listcc,listbcc,listdocument):
        #invio delle mail dal servizio v2 di Nios4
        try:
            self.err.error = False
            data = {}
            data['from'] = sendfrom
            data['fromName'] = sendfromname
            data['to'] = sendto
            data['subject'] = subject
            data['replyTo'] = replyto
            data['text'] = body
            if bodyhtml != "":
                data['html'] = bodyhtml
            data['cc'] = listcc
            data['bcc'] = listbcc

            #gestione degli allegati da fare
            url = f"https://app.pocketsell.com/_master/?action=email_send&token={self.__token}&db={dbname}"

            response = requests.post(url, json=data)

            if response.status_code == 200:
                return True
            else:
                self.err.errorcode = response.status_code
                self.err.errormessage = response.text
                return False

        except requests.RequestException as e:
            self.err.errorcode = "E014"
            self.err.errormessage = str(e)
            return False

    #----------------------------------------------------------------------------
    def send_templatemail(self,mail,idtemplate,payload):
        #invio di una mail attraverso le notifiche
        dimail = {}
        dimail["MAIL"] = mail
        dimail["IDTEMP"] = idtemplate
        dimail["VALTEMP"] = payload

        gguid = uuid.uuid4()
        tid = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        param = self.convap(json.dumps(dimail,ensure_ascii=False))
        data = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        stringa = f"INSERT INTO so_notifications (gguid,gguidp,tid,eli,arc,ut,uta,exp,ind,tap,dsp,dsc,dsq1,dsq2,utc,tidc,param,repeat_b,notificationdescription,tdescription,noticedate,remindertype,dateb,notificationsystem,date,read_b,notificationtype,notificationtitle,ttitle) "    
        stringa2 = f"VALUES ('{gguid}','',{tid},0,0,'nios4.clock','','',0,'','','',0,0,'nios4.clock',{tid},'{param}',0,'','','{data}',0,'{data}','nios4','{data}',0,2,'','')"

        self.setsql(stringa + stringa2)
        self.addsyncbox("so_notifications",gguid)

    #----------------------------------------------------------------------------
    def download_file(self,dbname,pathfile,filename,tablename,fieldname,gguid):
         #procedo a salvare e a inviare un file al database
        #creo il dizionario {"gguidfile":"43bc669f-37ef-42fd-9fb3-70e4655330f6","nomefile":"C:\\Users\\Ilaria\\Downloads\\Esempio scheda lavoro.pdf","tid":"20241107142353"}
        gguidrif = str(uuid.uuid4())
        tid = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        dizionario = {"gguidfile":gguidrif,"nomefile":filename,"tid":tid}
        stringa = json.dumps(dizionario)
        #procedo a caricare fisicamente il file
        url = f"https://app.pocketsell.com/_sync/?action=file_upload&token={self.__token}&db={dbname}&dos=Windows&dmodel=desktop&gguid={gguidrif}&tablename={tablename}&type=file&system=nios4"
        headers = {
            "Content-Type": "xxx"
        }

        # Leggo il file in modalità binaria
        with open(pathfile, "rb") as file:
            file_data = file.read()

        # Invio la richiesta POST con il file come corpo della richiesta
        response = requests.post(url, headers=headers, data=file_data)

        # Converto la risposta in un dizionario (assumendo che la risposta sia in formato JSON)
        result = response.json()

        #procedo a salvare il valore
        self.setsql(f"UPDATE {tablename} SET {fieldname}='{self.convap(stringa)}',file_{fieldname}='{self.convap(filename)}',tid={self.tid()} WHERE gguid='{gguid}'")

        self.addsyncbox(tablename,gguid)

        return result
    #----------------------------------------------------------------------------

    def getsql(self,sql):
        return self.__db.getsql(sql)

    def addsyncbox(self,tablename,gguid):
        return self.__db.addsyncbox(tablename,gguid)

    def addcleanbox(self,tablename,gguid):
        return self.__db.addcleanbox(tablename,gguid)

    def setsql(self,sql):
        return self.__db.setsql(sql)
    
    def newrow(self,tablename,gguid):
        return self.__db.newrow(tablename,gguid)

    def tid(self):
        return self.__utility.tid(self)

    def gguid(self):
        return str(uuid.uuid4())

    def convap(self,value):
        if value == None:
            return ""
        valore =str(value).replace("'", "''")
        return valore

    def getind(self,tablename):
        return self.__db.get_ind(tablename)

    def encode_to_url(self,value):
        string_lower = value.lower()
        string_with_hyphens = string_lower.replace(' ', '-')
        return quote(string_with_hyphens, safe='')

    def login(self):
        #login server
        try:
            self.err.error = False
            url = ""    
            if self.__token:
                url = "https://app.pocketsell.com/_master/?action=user_login&token=" + self.__token
            else:
                url = "https://app.pocketsell.com/_master/?action=user_login&email=" + self.__username + "&password=" + self.__password

            req = urllib.request.Request(url)
            valori = json.load(urllib.request.urlopen(req))
            if valori["error"] == True:
                self.err.errorcode = valori["error_code"]
                self.err.errormessage = valori["error_message"]
                return None
            #set login value
            datiutente = valori["user"]
            self.__token = datiutente["token"]
            self.__idaccount = datiutente["id"]
            self.__mailaccount = datiutente["email"]
            return valori

        except Exception as e:
            self.err.errorcode = "E014"
            self.err.errormessage = str(e)
            return None

    def download_datablock(self,dbname,TID,countrows):
        #receive datablock
        #sendstring = "https://www.nios4.com/_sync/?action=sync_all&token=" + self.__token + "&db=" & + dbname + "&tid_sync=" + str(TID) + "&dos=Linux&dmodel=desktop&partial=" + str(self.nrow_sync) + "&partial_from=" + str(countrows)
        sendstring = f"https://app.pocketsell.com/_sync/?action=sync_all&token={self.__token}&db={dbname}&tid_sync={str(TID)}&dos=Linux&dmodel=desktop&partial={str(self.nrow_sync)}&partial_from={str(countrows)}"
        
        datablock = {}
        s = [""]
        datablock["XXX"] = s

        datablock = urllib.parse.urlencode(datablock).encode()
        req =  urllib.request.Request(sendstring, data=datablock)
        resp = json.load(urllib.request.urlopen(req))

        if resp["result"] == "KO":
            self.err.errorcode = resp["code"]
            self.err.errormessage = resp["message"]
            return None

        return resp

    def upload_datablock(self,datablock,dbname,TID,partial):
        #send datablock
        itype=0
        if partial == True:
            itype=1

        sendstring = "https://app.pocketsell.com/_sync/?action=sync_all&token=" + self.__token + "&db=" + dbname + "&tid_sync=" + self.__utility.float_to_str(self,TID) + "&dos=Windows&dmodel=python&partial_send=" + str(itype)
        
        #datablock = urllib.parse.urlencode(datablock).encode()
        #req =  urllib.request.Request(sendstring, data=datablock)
        #resp = json.load(urllib.request.urlopen(req))

        #with open('/home/nios4ai/sync_nios4/received_data.json', 'w') as file:
        #    json.dump(datablock, file, indent=4) 


        resp = requests.post(sendstring, json=datablock)

        #print(datablock)
        response = resp.json()

        if response["result"] == "KO":
            self.err.errorcode = response["code"]
            self.err.errormessage = response["message"]
            return None

        return response

    def extract_syncrow(self,tablename,record,columns):
        #extract data row for syncbox
        refieldforbidden={}
        refieldforbidden["read_b"] = "read"
        refieldforbidden["usercloud_b"] = "usercloud"
        refieldforbidden["repeat_b"] = "repeat"

        count = 0
        o = {}
        cvalue = {}
        o["command"] ="insert"
        o["tablename"] =tablename
        o["client"] =0
        for nc in columns:
            
            if nc == "gguid" or nc =="tid" or nc=="arc" or nc=="uta" or nc=="ut":
                o[nc] = record[count]    
            
            if nc in refieldforbidden:
                nc = refieldforbidden[nc]

            cvalue[nc] = record[count]

            #devo controllare se il valore è una data, se si lo devo convertire
            if type(cvalue[nc]) == datetime:
                if cvalue[nc] is None:
                    cvalue[nc] = 0
                else:
                    cvalue[nc] = int(cvalue[nc].strftime('%Y%m%d%H%M%S'))

            count = count+1

        o["cvalues"] = json.dumps(cvalue, ensure_ascii=False)
        return o

    def install_data(self,useNTID,datablock,managefile,skipusers,reworkdata):
        #install datablock in database
        actualtables = self.__db.get_tablesname()
        actualfields = self.__db.get_fieldsname()
        actualusers = self.__db.get_gguid("so_users")

        #--------------------------------------------
        #Head of data
        #--------------------------------------------
        if "data" in datablock:
            datahead = datablock["data"]
            print(self.stime() +  "     SEED->" + datahead["SEED"])
        #--------------------------------------------
        #TODO delete file to server
        #--------------------------------------------

        #--------------------------------------------
        #TODO Initial conditions
        #--------------------------------------------

        #--------------------------------------------
        #Delete tables
        #--------------------------------------------
        reloadtables= False
        if "clean_tables" in datablock:
            if type(datablock["clean_tables"]) is list:
                for dtable in datablock["clean_tables"]:
                    if dtable != "":
                        if dtable in actualtables:
                            if self.__db.exists_table(dtable) == True:
                                if self.viewmessage == True:
                                    print(self.stime() +  "     delete table " + dtable)
                                if self.__db.setsql("DELETE FROM so_tables WHERE tablename='" + dtable + "'") == False:
                                    return False
                                if self.__db.setsql("DELETE FROM so_fields WHERE tablename='" + dtable + "'") == False:
                                    return False
                                if self.__db.setsql("DROP TABLE " + dtable) == False:
                                    return False
                                reloadtables = True

        #--------------------------------------------
        #Delete fields
        #--------------------------------------------
        reloadfields = False
        if "clean_fields" in datablock:
            for key in datablock["clean_fields"].keys():
                if key in actualtables: #key nome della tabella
                    reloadfields = True
                    if self.viewmessage == True:
                        print(self.stime() +  "     delete field " + str(datablock["clean_fields"][key]) + " from table " + key)

                    for fieldname in datablock["clean_fields"][key]:
                        if self.__db.exists_field(key,fieldname) == True:
                            if self.__db.setsql(f"ALTER TABLE {key} DROP COLUMN {fieldname}") == False:
                                return False
                            if self.__db.setsql(f"DELETE FROM so_fields WHERE tablename='{key}' AND fieldname='{fieldname}'") == False:
                                return False

        #--------------------------------------------
        if reloadtables == True or reloadfields == True:
            actualtables = self.__db.get_tablesname()
            actualfields = self.__db.get_fieldsname()      
        reloadtables = False
        reloadfields = False
        #--------------------------------------------
        #tables
        #--------------------------------------------
        enabledtables = []
        if len(self.enabled_create_tables) > 0 or len(self.enabled_getdata_tables) > 0 or len(self.enabled_setdata_tables) > 0:
            if "so_localusers" not in self.enabled_create_tables:
                enabledtables.append("so_localusers")
            
            for t in self.enabled_create_tables:
                if t not in enabledtables and t != "":
                    enabledtables.append(t)
            
            for t in self.enabled_getdata_tables:
                if t not in enabledtables  and t != "":
                    enabledtables.append(t)

            for t in self.enabled_setdata_tables:
                if t not in enabledtables  and t != "":
                    enabledtables.append(t)
        #--------------------------------------------
        if "tables" in datablock:
            if type(datablock["tables"]) is list:
                for table in datablock["tables"]:
                    vtable = True
                    if len(enabledtables) > 0:
                        if table["tablename"] not in enabledtables:
                            vtable = False
                    if table["tablename"] != "" and vtable == True:
                        #create table in database
                        key = str(table["tablename"]).lower()

                        if table["tablename"] not in actualtables:
                            reloadtables = True
                            if self.viewmessage == True:
                                print(self.stime() +  "     add table " + table["tablename"])
                            #if self.__db.setsql("CREATE TABLE " + key + " (gguid VARCHAR(40) Not NULL DEFAULT '', tid DOUBLE NOT NULL DEFAULT 0,eli INTEGER NOT NULL DEFAULT 0,arc INTEGER NOT NULL DEFAULT 0,ut VARCHAR(255) NOT NULL DEFAULT '',uta VARCHAR(255) NOT NULL DEFAULT '',exp TEXT NOT NULL DEFAULT '',gguidp VARCHAR(40) NOT NULL DEFAULT '', ind INTEGER NOT NULL DEFAULT 0,tap TEXT NOT NULL DEFAULT '',dsp TEXT NOT NULL DEFAULT '',dsc TEXT NOT NULL DEFAULT '', dsq1 DOUBLE NOT NULL DEFAULT 0, dsq2 DOUBLE NOT NULL DEFAULT 0,utc VARCHAR(255) NOT NULL DEFAULT '', tidc DOUBLE NOT NULL DEFAULT 0,xxx_yyy TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)") == False:
                            if self.__db.setsql("CREATE TABLE " + key + " (gguid VARCHAR(40) Not NULL DEFAULT '', tid DOUBLE NOT NULL DEFAULT 0,eli INTEGER NOT NULL DEFAULT 0,arc INTEGER NOT NULL DEFAULT 0,ut VARCHAR(255) NOT NULL DEFAULT '',uta VARCHAR(255) NOT NULL DEFAULT '',exp TEXT NOT NULL DEFAULT '',gguidp VARCHAR(40) NOT NULL DEFAULT '', ind INTEGER NOT NULL DEFAULT 0,tap TEXT NOT NULL DEFAULT '',dsp TEXT NOT NULL DEFAULT '',dsc TEXT NOT NULL DEFAULT '', dsq1 DOUBLE NOT NULL DEFAULT 0, dsq2 DOUBLE NOT NULL DEFAULT 0,utc VARCHAR(255) NOT NULL DEFAULT '', tidc DOUBLE NOT NULL DEFAULT 0)") == False:
                                return False
                            #if self.__db.setsql("CREATE INDEX newindex_" + key + " ON " + key + " (gguid,gguidp)") == False:
                            #    return False
                            if self.__db.setsql("INSERT INTO so_tables (GGUID,tablename,param,expressions,tablelabel,newlabel,lgroup) VALUES ('{0}','{1}','','','','','')".format(str(table["gguid"]),key)) == False:
                                return False
                            actualtables[key] = 0

                        if actualtables[key] < table["tid"]:
                            reloadtables = True
                            if self.viewmessage == True:
                                print(self.stime() +  "     update table " + table["tablename"])
                            sqlstring = ""
                            if useNTID == False:
                                sqlstring = "UPDATE so_tables SET tid=" + self.__utility.float_to_str(self,table["tid"]) + ","
                            else:
                                sqlstring = "UPDATE so_tables SET tid=" + self.__utility.float_to_str(self,self.__utility.tid(self) + 10) + ","
                            
                            sqlstring = sqlstring + "eli=" + str(table["eli"]) + ","
                            sqlstring = sqlstring + "arc=" + str(table["arc"]) + ","
                            sqlstring = sqlstring + "ut='" + str(table["ut"]) + "',"
                            sqlstring = sqlstring + "eliminable=" + str(table["eliminable"]) + ","
                            sqlstring = sqlstring + "editable=" + str(table["editable"]) + ","
                            sqlstring = sqlstring + "displayable=" + str(table["displayable"]) + ","
                            sqlstring = sqlstring + "syncsel=" + str(table["syncsel"]) + ","
                            sqlstring = sqlstring + "syncyes=" + str(table["syncyes"]) + ","
                            sqlstring = sqlstring + "tablename='" + table["tablename"] + "',"
                            if "lgroup" in table:
                                sqlstring = sqlstring + "lgroup='" + self.__utility.convap(self,table["lgroup"]) + "',"
                            else:
                                sqlstring = sqlstring + "lgroup=''"
                            if "param" in table:
                                sqlstring = sqlstring + "param='" + self.__utility.convap(self,table["param"]) + "',"
                            else:
                                sqlstring = sqlstring + "param='',"
                            if "expressions" in table:
                                sqlstring = sqlstring + "expressions='" + self.__utility.convap(self,table["expressions"]) + "',"
                            else:
                                sqlstring = sqlstring + "expressions='',"
                            
                            sqlstring = sqlstring + "newlabel='" + self.__utility.convap(self,table["newlabel"]) + "',"
                            sqlstring = sqlstring + "tablelabel='" + self.__utility.convap(self,table["tablelabel"]) + "'"
                            sqlstring = sqlstring + " WHERE tablename='" + table["tablename"] + "'"

                            if self.__db.setsql(sqlstring) == False:
                                return False

                        #break #--------
        #--------------------------------------------
        #fields
        #--------------------------------------------
        #fields to skip
        fieldforbidden={}
        fieldforbidden["read"] = "read_b"
        fieldforbidden["usercloud"] = "usercloud_b"
        fieldforbidden["repeat"] = "repeat_b"

        if "fields" in datablock:
            if type(datablock["fields"]) is list:
                for field in datablock["fields"]:
                    if str(field["fieldname"]) != "" and str(field["fieldname"]) != "system" and str(field["tablename"]) != "" and field["tablename"] in actualtables:
                        #check special fields
                        fieldtype = field["fieldtype"]
                        if fieldtype == 5:
                            fields_currency = 1
                
                        if field["fieldname"].lower() in fieldforbidden:
                            field["fieldname"] = fieldforbidden[field["fieldname"]]

                        key =  field["tablename"].lower() + "|" + field["fieldname"].lower()

                        if key not in actualfields and str(field["fieldname"]).lower():
                            reloadfields = True
                            if self.viewmessage == True:
                                print(self.stime() +  "     add field " +  field["fieldname"] + "(" + field["tablename"] + ")")
                            #create the field inside the table
                            sqlstring = ""
                            sqlstring2 = ""
                            #text field
                            if fieldtype == 0 or fieldtype == 1 or fieldtype == 2 or fieldtype == 30 or fieldtype == 14 or fieldtype == 12 or fieldtype == 15 or fieldtype == 34:
                                #special field
                                sqlstring = "ALTER TABLE " + str(field["tablename"]).lower() + " ADD " + str(field["fieldname"]).lower() + " MEDIUMTEXT NOT NULL DEFAULT ''"
                                sqlstring2 = "UPDATE " + str(field["tablename"]).lower()  + " SET " + str(field["fieldname"]).lower() + "=''"

                            if fieldtype == 20 or fieldtype == 22 or fieldtype == 21 or fieldtype == 24 or fieldtype == 25 or fieldtype == 26 or fieldtype == 27  or fieldtype == 28  or fieldtype == 29  or fieldtype == 31  or fieldtype == 32:
                                sqlstring = "ALTER TABLE " + str(field["tablename"]).lower() + " ADD " + str(field["fieldname"]).lower() + " MEDIUMTEXT NOT NULL DEFAULT ''"
                                sqlstring2 = "UPDATE " + str(field["tablename"]).lower()  + " SET " + str(field["fieldname"]).lower() + "=''"
                            #field double
                            if fieldtype == 3 or fieldtype == 5 or fieldtype == 10 or fieldtype == 17:
                                sqlstring = "ALTER TABLE " + str(field["tablename"]).lower() + " ADD " + str(field["fieldname"]).lower() + " DOUBLE NOT NULL DEFAULT 0"
                                sqlstring2 = "UPDATE " + str(field["tablename"]).lower()  + " SET " + str(field["fieldname"]).lower() + "=0"
                            #field date
                            if fieldtype == 18:
                                sqlstring = "ALTER TABLE " + str(field["tablename"]).lower() + " ADD " + str(field["fieldname"]).lower() + " DATETIME"
                                sqlstring2 = "UPDATE " + str(field["tablename"]).lower()  + " SET " + str(field["fieldname"]).lower() + "=NULL"
                            #field integer
                            if fieldtype == 4 or fieldtype == 9 or fieldtype == 6:
                                sqlstring = "ALTER TABLE " + str(field["tablename"]).lower() + " ADD " + str(field["fieldname"]).lower() + " INTEGER NOT NULL DEFAULT 0"
                                sqlstring2 = "UPDATE " + str(field["tablename"]).lower()  + " SET " + str(field["fieldname"]).lower() + "=0"

                            if fieldtype == "" and fieldtype !=11:
                                self.err.errorcode = "E001"
                                self.err.errormessage = "CAMPO " + str(fieldtype) + " NON GESTITO!"
                                return False

                            if sqlstring != "":
                                if self.__db.setsql(sqlstring) == False:
                                    return False

                            if sqlstring2 != "":
                                if self.__db.setsql(sqlstring2) == False:
                                    return False
                            #add special field
                            if fieldtype == 20 or fieldtype == 22:
                                if self.__db.setsql("ALTER TABLE " + str(field["tablename"]).lower() + " ADD gguid_" + str(field["fieldname"]).lower() + " TEXT") == False:
                                    return False
                                if self.__db.setsql("UPDATE " + str(field["tablename"]).lower()  + " SET gguid_" + str(field["fieldname"]).lower() + "=''") == False:
                                    return False
                            
                            if fieldtype == 21 or fieldtype == 24:
                                if self.__db.setsql("ALTER TABLE " + str(field["tablename"]).lower() + " ADD dat_" + str(field["fieldname"]).lower() + " TEXT") == False:
                                    return False
                                if self.__db.setsql("UPDATE " + str(field["tablename"]).lower()  + " SET dat_" + str(field["fieldname"]).lower() + "=''") == False:
                                    return False

                            if fieldtype == 28:
                                if self.__db.setsql("ALTER TABLE " + str(field["tablename"]).lower() + " ADD file_" + str(field["fieldname"]).lower() + " TEXT") == False:
                                    return False
                                if self.__db.setsql("UPDATE " + str(field["tablename"]).lower()  + " SET file_" + str(field["fieldname"]).lower() + "=''") == False:
                                    return False

                            if fieldtype == 24:
                                if self.__db.setsql("ALTER TABLE " + str(field["tablename"]).lower() + " ADD lat_" + str(field["fieldname"]).lower() + " DOUBLE NOT NULL DEFAULT 0") == False:
                                    return False
                                if self.__db.setsql("UPDATE " + str(field["tablename"]).lower()  + " SET lat_" + str(field["fieldname"]).lower() + "=0") == False:
                                    return False
                                if self.__db.setsql("ALTER TABLE " + str(field["tablename"]).lower() + " ADD lng_" + str(field["fieldname"]).lower() + " DOUBLE NOT NULL DEFAULT 0") == False:
                                    return False
                                if self.__db.setsql("UPDATE " + str(field["tablename"]).lower()  + " SET lng_" + str(field["fieldname"]).lower() + "=0") == False:
                                    return False

                            if self.__db.setsql("INSERT INTO so_fields (fieldlabel2,panel,style,expression,param,fieldlabel,ut,gguid,tablename,fieldname) VALUES ('','','','','','','','{0}','{1}','{2}')".format(str(field["gguid"]),str(field["tablename"]).lower(),str(field["fieldname"]).lower())) == False:
                                return False
                            
                            actualfields[key] =[0,fieldtype]
                            
                        if actualfields[key][0] < field["tid"]:
                            reloadfields = True
                            if self.viewmessage == True:
                                print(self.stime() +  "     update field " +  field["fieldname"] + "(" + field["tablename"] + ")")

                            sqlstring = ""
                            if useNTID == False:
                                sqlstring = "UPDATE so_fields SET tid=" + self.__utility.float_to_str(self,field["tid"]) + ","
                            else:
                                sqlstring = "UPDATE so_fields SET tid=" + self.__utility.float_to_str(self,self.__utility.tid(self) + 10) + ","
                            sqlstring = sqlstring + "eli=" + str(field["eli"]) + ","
                            sqlstring = sqlstring + "arc=" + str(field["arc"]) + ","
                            sqlstring = sqlstring + "ut='" + str(field["ut"]) + "',"
                            sqlstring = sqlstring + "eliminable=" + str(field["eliminable"]) + ","
                            sqlstring = sqlstring + "editable=" + str(field["editable"]) + ","
                            sqlstring = sqlstring + "displayable='" + str(field["displayable"]) + "',"
                            sqlstring = sqlstring + "obligatory=" + str(field["obligatory"]) + ","
                            sqlstring = sqlstring + "viewcolumn=" + str(field["viewcolumn"]) + ","
                            sqlstring = sqlstring + "ind=" + str(field["ind"]) + ","
                            sqlstring = sqlstring + "columnindex=" + str(field["columnindex"]) + ","
                            sqlstring = sqlstring + "fieldtype=" + str(field["fieldtype"]) + ","
                            sqlstring = sqlstring + "columnwidth=" + str(field["columnwidth"]) + ","
                            sqlstring = sqlstring + "ofsystem=" + str(field["ofsystem"]) + ","
                            sqlstring = sqlstring + "panel='" + field["panel"] + "',"
                            sqlstring = sqlstring + "panelindex=" + str(field["panelindex"]) + ","
                            sqlstring = sqlstring + "tablename='" + field["tablename"] + "',"
                            sqlstring = sqlstring + "fieldname='" + field["fieldname"] + "',"
                            
                            if field["style"].find("{") == -1:
                                sqlstring = sqlstring + "style='',"
                            else:
                                sqlstring = sqlstring + "style='" + self.__utility.convap(self,field["style"]) + "',"
                            
                            if field["param"].find("{") == -1:
                                sqlstring = sqlstring + "param='',"
                            else:
                                sqlstring = sqlstring + "param='" + self.__utility.convap(self,field["param"]) + "',"
                            
                            if field["expression"].find("{") == -1:
                                sqlstring = sqlstring + "expression='',"
                            else:
                                sqlstring = sqlstring + "expression='" + self.__utility.convap(self,field["expression"]) + "',"
                            
                            sqlstring = sqlstring + "fieldlabel='" + self.__utility.convap(self,field["fieldlabel"]) + "',"
                            sqlstring = sqlstring + "fieldlabel2='" + self.__utility.convap(self,field["fieldlabel2"]) + "'"
                            sqlstring = sqlstring + " WHERE tablename='" + str(field["tablename"]) + "' AND fieldname='" + str(field["fieldname"]) + "'"

                            if self.__db.setsql(sqlstring) == False:
                                return False
        #--------------------------------------------
        if reloadtables == True or reloadfields == True:
            actualtables = self.__db.get_tablesname()
            actualfields = self.__db.get_fieldsname()  
        #--------------------------------------------
        #users
        #--------------------------------------------
        if "users" in datablock:
            if type(datablock["users"]) is list:
                for user in datablock["users"]:
                    if user["gguid"] not in actualusers:
                        if self.__db.setsql("INSERT INTO so_users (GGUID,username,password_hash,param) VALUES ('{0}','','','')".format(str(user["gguid"]))) == False:
                            return False
                        actualusers[user["gguid"]] = 0

                    if actualusers[user["gguid"]] < user["tid"]:
                        
                        sqlstring = ""
                        if useNTID == False:
                            sqlstring = "UPDATE so_users SET tid=" + self.__utility.float_to_str(self,user["tid"]) + ","
                        else:
                            sqlstring = "UPDATE so_users SET tid=" + self.__utility.float_to_str(self,self.__utility.tid(self) + 10) + ","                            

                        sqlstring = sqlstring + "eli=" + str(user["eli"]) + ","
                        sqlstring = sqlstring + "arc=" + str(user["arc"]) + ","
                        sqlstring = sqlstring + "admin=" + str(user["admin"]) + ","
                        sqlstring = sqlstring + "id=" + str(user["id"]) + ","
                        sqlstring = sqlstring + "ut='" + str(user["ut"]) + "',"
                        sqlstring = sqlstring + "username='" + str(user["username"]) + "',"
                        sqlstring = sqlstring + "password_hash='" + str(user["password_hash"]) + "',"

                        if str(user["param"]).find("{") == -1:
                            sqlstring = sqlstring + "param='',"
                        else:
                            sqlstring = sqlstring + "param='" + self.__utility.convap(self,str(user["param"])) + "',"

                        sqlstring = sqlstring + "categories=" + str(user["categories"])
                        sqlstring = sqlstring + " WHERE gguid='" + str(user["gguid"]) + "'"
                        
                        if self.__db.setsql(sqlstring) == False:
                            return False

                        records = self.__db.getsql("SELECT gguid FROM so_localusers where gguid='{0}'".format(str(user["gguid"])))
                        if records == None:
                            return False
                        if len(records) == 0:

                            password_hash = ""
                            if user["password_hash"] != None:
                                password_hash =  self.__utility.convap(self,user["password_hash"])

                            sqlstring = "INSERT INTO so_localusers("
                            sqlstring = sqlstring + "gguid," #0
                            sqlstring = sqlstring + "tid," #1
                            sqlstring = sqlstring + "eli," #2
                            sqlstring = sqlstring + "arc," #3
                            sqlstring = sqlstring + "ut," #4
                            sqlstring = sqlstring + "uta," #5
                            sqlstring = sqlstring + "exp," #6
                            sqlstring = sqlstring + "gguidp," #7
                            sqlstring = sqlstring + "ind," #8
                            sqlstring = sqlstring + "username," #9
                            sqlstring = sqlstring + "optionsbase," #10
                            sqlstring = sqlstring + "optionsadmin," #11
                            sqlstring = sqlstring + "param," #12
                            sqlstring = sqlstring + "usermail," #13
                            sqlstring = sqlstring + "color," #14
                            sqlstring = sqlstring + "id," #15
                            sqlstring = sqlstring + "tap," #16
                            sqlstring = sqlstring + "dsp," #17
                            sqlstring = sqlstring + "dsc," #18
                            sqlstring = sqlstring + "dsq1," #19
                            sqlstring = sqlstring + "dsq2," #20
                            sqlstring = sqlstring + "utc," #21
                            sqlstring = sqlstring + "tidc," #22
                            sqlstring = sqlstring + "password_hash," #23
                            sqlstring = sqlstring + "usercloud_b," #24
                            sqlstring = sqlstring + "admin," #25
                            sqlstring = sqlstring + "categories," #26
                            #----------------------------------
                            sqlstring = sqlstring[:-1] + ")"
                            #----------------------------------
                            sqlstring = sqlstring + " VALUES('" + str(user["gguid"]) + "'," #0
                            sqlstring = sqlstring + "0" + "," #1
                            sqlstring = sqlstring + "0," #2
                            sqlstring = sqlstring + "0," #3
                            sqlstring = sqlstring + "'" + self.__utility.convap(self,str(self.__username)) + "'," #4
                            sqlstring = sqlstring + "''," #5
                            sqlstring = sqlstring + "''," #6
                            sqlstring = sqlstring + "''," #7
                            sqlstring = sqlstring + "0," #8
                            sqlstring = sqlstring + "'" + self.__utility.convap(self,str(user["username"])) + "'," #9
                            sqlstring = sqlstring + "0," #10
                            sqlstring = sqlstring + "0," #11
                            sqlstring = sqlstring + "'{}'," #12
                            sqlstring = sqlstring + "''," #13
                            sqlstring = sqlstring + "-1," #14
                            sqlstring = sqlstring + str(user["id"]) + "," #15
                            sqlstring = sqlstring + "''," #16
                            sqlstring = sqlstring + "''," #17
                            sqlstring = sqlstring + "''," #18
                            sqlstring = sqlstring + "0," #19
                            sqlstring = sqlstring + "0," #20
                            sqlstring = sqlstring + "'" + str(self.__username) + "'," #21
                            sqlstring = sqlstring + str(self.__utility.tid(self)) + "," #22
                            sqlstring = sqlstring + "'" + password_hash + "'," #23
                            sqlstring = sqlstring + "1," #25
                            sqlstring = sqlstring + str(user["admin"]) + ","  #25
                            sqlstring = sqlstring + str(user["categories"]) + "," #26
                            #----------------------------------
                            sqlstring =  sqlstring[:-1] + ")"
                            #----------------------------------
                            if self.__db.setsql(sqlstring) == False:
                                return False

        #--------------------------------------------
        #syncbox
        #--------------------------------------------
        if "sync_box" in datablock:
            if type(datablock["sync_box"]) is list:

                #extract tables to sync
                tables = {}
                for row in datablock["sync_box"]:
                    vtable = True
                    if len(self.enabled_getdata_tables) > 0:
                        if row["tablename"] not in self.enabled_getdata_tables:
                            vtable = False
                    if vtable == True:
                        if row["tablename"] not in tables:
                            tables[row["tablename"]] = self.__db.get_gguid(row["tablename"])

                for row in datablock["sync_box"]:
                    if row["command"]  == "insert":
                        if row["tablename"] in tables:

                            tc = tables[row["tablename"]]
                            if tc is not None:
                                if row["gguid"] not in tc:

                                    if self.viewmessage == True:
                                        print(self.stime() +  "     add new row ("+row["tablename"]+")")

                                    self.__db.newrow(row["tablename"],row["gguid"])
                                    
                                    tc[row["gguid"]] = 0

                                if tc[row["gguid"]] < row["tid"]:

                                    if self.viewmessage == True:
                                        print(self.stime() +  "     update row ("+row["tablename"]+")")
                                
                                    sqlstring = "UPDATE " + row["tablename"] + " SET "
                                    va = json.loads(row["cvalues"])
                                    for key in va:
                                        value = va[key]
                                        if value != None:
                                            nc = key.lower()
                                            k = row["tablename"].lower() + "|" + nc

                                            if nc in fieldforbidden:
                                                nc = fieldforbidden[nc]

                                            #print(actualfields)
                                            #sys.exit("")

                                            if k in actualfields and key != "gguid":
                                                tca = actualfields[k][1]
                                                if tca != 11:
                                                    if nc == "gguid" or nc == "ut" or nc == "uta" or nc == "exp" or nc == "gguidp" or nc == "tap" or nc == "dsp" or nc == "dsc" or nc == "utc":
                                                        sqlstring = sqlstring + nc + "='" + self.__utility.convap(self,value) + "',"
                                                    elif nc == "eli" or nc == "arc" or nc == "ind" or nc == "dsq1" or nc == "dsq2" or nc == "tidc":
                                                        sqlstring = sqlstring + nc + "='" + str(value).replace(",",".") + "',"
                                                    elif nc == "tid":
                                                        if useNTID == False:
                                                            sqlstring = sqlstring + " tid=" + self.__utility.float_to_str(self,value) + ","
                                                        else:
                                                            sqlstring = sqlstring + " tid=" + self.__utility.float_to_str(self.__utility.tid(self) + 10) + ","
                                                    else:
                                                        if tca==0 or tca==1 or tca==2 or tca==30 or tca==14 or tca==12 or tca==11 or tca==15 or tca==20 or tca==21 or tca==22 or tca==24 or tca==25 or tca==26 or tca==27 or tca==28 or tca==29 or tca==31 or tca==32 or tca==34:
                                                            sqlstring = sqlstring + nc + "='" + self.__utility.convap(self,value.replace("'","`")) + "',"
                                                        if tca==3 or tca==5 or tca==10 or tca==9 or tca==17 or tca==6 or tca==4:
                                                            sqlstring = sqlstring + nc + "='" + str(value).replace(",",".") + "',"
                                                        if tca==18: #data
                                                            if value == "null":
                                                                value = 0
                                                            if type(value) == str and value != None:
                                                                value=float(value)                                                            
                                                            if value != 0:
                                                                #print("nc = " + str(round(value)) + " gguid = " + row["gguid"] + " tabella =" + row["tablename"].lower())
                                                                try:
                                                                    data_formato_mysql = datetime.strptime(str(round(value)), '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
                                                                    sqlstring = sqlstring + nc + "='" + data_formato_mysql + "',"
                                                                except Exception as e:
                                                                    print("errore formato data")
                                    
                                    sqlstring =  sqlstring[:-1] + " WHERE gguid='" + row["gguid"] + "'"

                                    #if row["gguid"] == "1192f785-35eb-4a87-98fb-927d033661a4":
                                    #print(sqlstring)

                                    if self.__db.setsql(sqlstring) == False:
                                        return False
                                    
                    if row["command"]  == "delete":
                        if row["tablename"] in tables:
                            sqlstring = "DELETE FROM " + row["tablename"] + " WHERE gguid='" + row["gguid"] + "'"
                            if self.__db.setsql(sqlstring) == False:
                                return False

        return True

    def stime(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def syncro(self,dbname,start_tid=None):

        if self.__token == "":
            self.err.errorcode = "E019"
            self.err.errormessage = "Please login first to synchronize"
            return False                

        print("--------------------------------------------------------------------")
        print(self.stime() +  "     START SYNC")
        print("--------------------------------------------------------------------")

        #-----------------------------------------------------------------------------
        #extract last sync tid
        #-----------------------------------------------------------------------------
        TID_db = 0
        if start_tid == None:
            records = self.__db.getsql("SELECT tidsync FROM lo_setting WHERE gguid='0'")
            if len(records) > 0:
                TID_db=records[0][0]
        else:
            TID_db = start_tid

        TID_start = self.__utility.tid(self)

        TID = TID_db

        if self.viewmessage == True:
            print(self.stime() +  "     TIDDB     -> " + str(TID_db))
            print(self.stime() +  "     TID_start -> " + str(TID_start))

        #-----------------------------------------------------------------------------
        #extract db structure
        #-----------------------------------------------------------------------------
        sync_tables = self.__db.extract_sotables("so_tables",TID)
        if sync_tables == None:
            return False
        if self.viewmessage == True:
            print(self.stime() +  "     STR.TABLE -> " + str(len(sync_tables)))

        sync_fields = self.__db.extract_sotables("so_fields",TID)

        if sync_fields == None:
            return False
        if self.viewmessage == True:
            print(self.stime() +  "     STR.FIELDS-> " + str(len(sync_fields)))


        sync_users = self.__db.extract_sotables("so_users",TID)
        if sync_users == None:
            return False
        if self.viewmessage == True:
            print(self.stime() +  "     STR.USERS -> " + str(len(sync_users)))            

        #-----------------------------------------------------------------------------
        #send structure
        #-----------------------------------------------------------------------------
        print(self.stime() +  "     SEND STRUCTURE DB")

        finaldata = {}
        finaldata["tables"] = sync_tables
        finaldata["fields"] = sync_fields
        finaldata["users"] = sync_users

        values= self.upload_datablock(finaldata,dbname,TID,True)
        if values == None:
            return False

        finaldata.clear()
        #partialdata = list()
        partialdata = []
        TID_index =0
        #-----------------------------------------------------------------------------
        #send cleanbox
        #-----------------------------------------------------------------------------
        if self.viewmessage == True:
            print(self.stime() +  "     SEND CLEANBOX")

        records = self.__db.getsql("SELECT gguidrif,tid,tablename FROM lo_cleanbox ORDER BY tid")
        if records == None:
            return False
        for r in records:
            o={}
            o["gguid"] = r[0]
            o["tid"] = r[1]
            o["arc"] = 0
            o["ut"] = ""
            o["uta"] = ""
            o["client"] = "0"
            o["tablename"] = r[2]
            o["command"] = "delete"
            partialdata.append(o)
            if len(partialdata) >= self.nrow_sync:
                finaldata["sync_box"] = partialdata
                values = self.upload_datablock(finaldata,dbname,TID,True)
                if values == None:
                    return False
                if TID_index <= values["tid_sync"]:
                    TID_index = values["tid_sync"]
                partialdata = list()
                finaldata.clear()

        #-----------------------------------------------------------------------------
        #extract data tables to send
        #-----------------------------------------------------------------------------
        table_syncbox = self.__db.getsql("SELECT tablename,gguidrif FROM lo_syncbox")

        tables = []
        records = self.__db.getsql("SELECT tablename FROM so_tables where eli=0  ORDER BY ind")
        if records == None:
            return False
        for r in records:
            tables.append(r[0])

        tableswdata=[]
        for t in tables:
            #controllo che sia abilitata
            vtable = True
            if len(self.enabled_setdata_tables) > 0:
                if t not in self.enabled_setdata_tables:
                    vtable = False

            #records = self.__db.getsql("SELECT COUNT(tid) as conta FROM " + t + " GROUP BY tid HAVING tid >=" + self.__utility.float_to_str(self,TID))
            if vtable == True:
                records = self.__db.getsql("SELECT COUNT(gguid) as conta FROM " + t + " WHERE tid >=" + self.__utility.float_to_str(self,TID))
                if records == None:
                    return False
                #if len(records) > 0:
                #    print(t + " " + str(len(records)))
                for r in records:
                    if r[0] > 0 and not t in tableswdata:
                        tableswdata.append(t)

        #aggiungo le tabelle richiamata dalla syncbox
        for rsyncbox in table_syncbox:
            if rsyncbox[0] not in tableswdata and rsyncbox[0] !="":
                tableswdata.append(rsyncbox[0])
        #-----------------------------------------------------------------------------
        #send split data
        #-----------------------------------------------------------------------------
        firstrows = []
        finaldata.clear()

        for tablename in tableswdata:
            
            #record derivati dall'aggiornamento del valore di tid
            records = self.__db.getsql("SELECT * FROM " + tablename + " where tid >=" + self.__utility.float_to_str(self,TID) + "  ORDER BY ind")
            if records == None:
                return False
            
            columns = self.__db.get_columnsname(tablename)
            if columns == None:
                return False
            
            for r in records:
                votorecord = True
                #controllo che il record non sia richiamato dalla syncbox
                for rsyncbox in table_syncbox:
                    if rsyncbox[0] == tablename and rsyncbox[1] == r[0]:
                        votorecord = False
                        break
                #create a dictionary of datas
                if votorecord == True:
                    o = self.extract_syncrow(tablename,r,columns)
                    if o == None:
                        return False
                    if len(firstrows) < 10:
                        firstrows.append(o)
                    else:
                        partialdata.append(o)

                    if len(partialdata) >= self.nrow_sync:
                        finaldata["sync_box"] = partialdata
                        if self.viewmessage == True:
                            print("send packet")
                        values = self.upload_datablock(finaldata,dbname,TID,True)
                        if values == None:
                            return False
                        if TID_index <= values["tid_sync"]:
                            TID_index = values["tid_sync"]
                        partialdata = list()
                        finaldata.clear()

            #record derivati dalla syncbox
            for rsyncbox in table_syncbox:
                if rsyncbox[0] == tablename:
                    records = self.__db.getsql(f"SELECT * FROM {tablename} where gguid='{rsyncbox[1]}'")
                    for r in records:
                        #create a dictionary of datas
                        o = self.extract_syncrow(tablename,r,columns)
                        if o == None:
                            return False
                        if len(firstrows) < 10:
                            firstrows.append(o)
                        else:
                            partialdata.append(o)

                        if len(partialdata) >= self.nrow_sync:
                            finaldata["sync_box"] = partialdata
                            if self.viewmessage == True:
                                print("send packet")
                            values = self.upload_datablock(finaldata,dbname,TID,True)
                            if values == None:
                                return False
                            if TID_index <= values["tid_sync"]:
                                TID_index = values["tid_sync"]
                            partialdata = list()
                            finaldata.clear()

        #send last block
        if len(partialdata) > 0:
            finaldata.clear()
            finaldata["sync_box"] = partialdata
            
            if self.viewmessage == True:
                print(self.stime() +  "     send last packet")
            
            values = self.upload_datablock(finaldata,dbname,TID,True)
            if values == None:
                return False
            if TID_index <= values["tid_sync"]:
                TID_index = values["tid_sync"]
            partialdata = list()
            finaldata.clear()

        #-----------------------------------------------------------------------------
        #Send first row
        #-----------------------------------------------------------------------------
        print(self.stime() +  "     START SYNCBOX")
        #print(firstrows)
        finaldata.clear()
        finaldata["sync_box"] = firstrows
        values = self.upload_datablock(finaldata,dbname,TID,False)
        if values == None:
            return False

        if  TID_db <= values["tid_sync"]:
            TID_db = values["tid_sync"]

        gfile = True
        ipartial = False
        if "partial" in values:
            if values["partial"] == True:
                gfile = False
                ipartial = True

        print(self.stime() +  "     install first packet")

        if self.install_data(False,values,gfile,False,False) == False:
            return False

        if ipartial == True:
            vcontinute = True
            count = self.nrow_sync
            while vcontinute == True:

                print(self.stime() +  "     receive partial packet")
                
                values = self.download_datablock(dbname,TID,count)
                if values == None:
                    return False
                if TID_db <= values["tid_sync"]:
                    TID_db = values["tid_sync"]
                gfile = True
                vcontinute = False
                if "partial" in values:
                    if values["partial"] == True:
                        gfile = False
                        vcontinute = True
                        count = count + self.nrow_sync

                if self.viewmessage == True:
                    print(self.stime() +  "     install partial packet")

                if self.install_data(False,values,gfile,False,False) == False:
                    return False

        self.__db.setsql("DELETE FROM lo_cleanbox")
        self.__db.setsql("DELETE FROM lo_syncbox")

        self.__db.setsql("UPDATE lo_setting SET tidsync=" + str(TID_db) + " WHERE gguid='0'")

        #-----------------------------------------------------------------------------
        #end
        #-----------------------------------------------------------------------------

        print("--------------------------------------------------------------------")
        print(self.stime() +  "     END SYNC")
        print("--------------------------------------------------------------------")
        return True
    #-----------------------------------------------------------------