import pyrebase
import time
import os
import RPi.GPIO
RPi.GPIO.setwarnings(False)
RPi.GPIO.setmode(RPi.GPIO.BOARD)
class set:
    def __init__(self,firebase_id,firebase_secret,device_name):
        self.fid = firebase_id
        self.fsecret = firebase_secret
        self.name = device_name
        self.os = os.name
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
    def auto(self,waittime,run):
        while True:
            self.getpins()
            if run == False:
                break
            time.sleep(waittime)
    def listen(self,str):
        value = self.database.child(str).get().val()
        return value
    def setdata(self,pin,value):
        self.database.child(self.name + "Connection").set(True)
    def info(self):
        return float(open("/sys/class/thermal/thermal_zone0/temp", "r").readline())
    def getpins(self):
        try:    
            if os.name == "posix":
                self.database.child(self.name + "_Connection").set(True)
                self.database.child(self.name + "_Temperature").set(self.info())
                value = self.database.child("pinsettings").get().val()
                pinlist = value.split("#")
                for itm in pinlist:
                    item = itm.split("$")
                    RPi.GPIO.setup(int(item[0]), RPi.GPIO.OUT)
                    if item[1] == "h":
                        RPi.GPIO.output(int(item[0]),RPi.GPIO.HIGH)
                        print("high")
                    elif item[1] == "l":
                        RPi.GPIO.output(int(item[0]),RPi.GPIO.LOW)
                        print("low")
                    
            else:
                print("Device is not a Raspberry.")
        except:
            time.sleep(3)
    def setpin(self,pin,value):
        print(pin + type(pin))
        print(value + type(value))
        RPi.GPIO.setup(pin, RPi.GPIO.OUT)
        if value == "h":
            RPi.GPIO.output(pin,RPi.GPIO.HIGH)
            print("high")
        elif value == "l":
            RPi.GPIO.output(pin,RPi.GPIO.LOW)
            print("low")