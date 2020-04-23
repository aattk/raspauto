import pyrebase
import time
import os
class login():
    def __init__(self,firebase_id,firebase_secret,device_name):
        self.fid = firebase_id
        self.fsecret = firebase_secret
        self.name = device_name
        config = {
            "apiKey": self.fsecret,
            "authDomain": self.fid+".firebaseapp.com",
            "databaseURL": "https://"+self.fid+".firebaseio.com",
            "storageBucket": self.fid+".appspot.com",
            #"serviceAccount": "path/to/serviceAccountCredentials.json"
        }
        firebase = pyrebase.initialize_app(config)
        self.database = firebase.database()
        print("Baglantı Kuruldu")
                
    def start(self,waittime,run):
        while True:
            try:    
                self.database.child(self.name + "Connection").set(True)
                if os.name == "nt":
                    value = self.database.child("pinsettings").get().val()
                    pinlist = value.split("#")
                    for itm in pinlist:
                        item = itm.split("$")
                        print(item[0] +" : "+item[1])
                    if run == False:
                        break
                    time.sleep(waittime)
                else:
                    print("Device is not a Raspberry.")
            except:
                time.sleep(3)
                continue
    def listen(self,str):
        value = self.database.child(str).get().val()
        return value
    def setpin(self,pin,value):
        self.database.child(self.name + "Connection").set(True)

        