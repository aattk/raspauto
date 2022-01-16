# -*- coding: utf-8 -*-
import time
import os
import subprocess
from threading import Thread
import telegram
import sqlite3 as sql

try:
    import RPi.GPIO as GPIO
    import picamera
except Exception as e:
    print("GPIO Library not found.")

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

class set:
    def __init__(self, telegram_id, password):
        self.tid = telegram_id
        self.password = password
        self.pins = []
        self.awatch = False
        self.aupdate = []
        self.acontext = []
        self.dbinit()
        self.pinKeyboardUpdate(1)
        self.updateInit()
        

    def updateInit(self):
        updater = Updater(self.tid, use_context=True)
        updater.dispatcher.add_handler(CommandHandler('start', self.start, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('pinadd', self.pinadd, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('pinlist', self.pin_list, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('pindelete', self.pinDelete, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('userdelete', self.user_delete, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('userlist', self.userList, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('rename', self.rename, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('restart', self.restart, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('photo', self.photo, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('alarmstart', self.alarmstart, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('alarmstop', self.alarmstop, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('temp',self.temp, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('code', self.code, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('commands', self.commands, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('libupdate', self.libupdate, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('alwayswatch', self.alwayswatch, run_async=True))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.button, run_async=True))
        updater.dispatcher.add_handler(CommandHandler('help',self.help_command, run_async=True))
        updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.emsg, run_async=True))
        updater.start_polling()
        updater.idle()

    def dbinit(self):
        if(not os.path.isfile("ra.sqlite")):
            db = sql.connect('ra.sqlite')
            im = db.cursor()
            im.execute("CREATE TABLE users (id, name)")
            im.execute("CREATE TABLE pins (id,name,state)")
            im.execute("CREATE TABLE alarm (id,state)")
            im.execute("CREATE TABLE language (lcode,data)")

    def saveUser(self,id,name):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("INSERT INTO users VALUES ('"+str(id)+"', '"+name+"')")
        db.commit()
        db.close()

    def readUsers(self):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("SELECT * FROM users")
        data = im.fetchall()
        db.close()
        return data

    def renameUser(self,id,name):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("UPDATE users SET name = '"+name+"' WHERE id='"+str(id)+"'")
        db.commit()
        db.close()

    def isLogin(self,id):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("SELECT * FROM users where id = '"+str(id)+"'")
        data = im.fetchall()
        db.close()
        if len(data) > 0:
            return True
        else:
            return False
    
    def savePin(self,data):
        data = data.split(" ")
        if len(data) > 1:
            db = sql.connect('ra.sqlite')
            im = db.cursor()
            im.execute("INSERT INTO pins VALUES ('"+str(data[2])+"', '"+str(data[1])+"','F')")
            db.commit()
            db.close()
            return True
        else: 
            return False

    def deletePin(self,id,query):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("SELECT * FROM pins where id = '"+str(id)+"'")
        data = im.fetchone()
        im.execute("DELETE FROM pins WHERE id = '"+str(id)+"'")
        query.edit_message_text(text= data[1] + " deleted.".format(query.data))
        db.commit()
        db.close()

    def deleteUser(self,id,query):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("SELECT * FROM users where id = '"+str(id)+"'")
        data = im.fetchone()
        im.execute("DELETE FROM users WHERE id = '"+str(id)+"'")
        query.edit_message_text(text= data[1] + " deleted.".format(query.data))
        db.commit()
        db.close()

    def updatePinState(self,id,query):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("SELECT * FROM pins where id = '"+str(id)+"'")
        data = im.fetchone()
        stt = ""
        if (data[2] == 'F'):
            stt = "T"
            try:
                GPIO.output(int(data[0]), GPIO.HIGH)
                query.edit_message_text(text=data[1] + " opened.".format(query.data))
            except Exception as e:
                print("GPIO Set Error")
                query.edit_message_text("Something went wrong.".format(query.data))
        elif (data[2] == 'T'):
            stt = "F"
            try:
                GPIO.output(int(data[0]), GPIO.LOW)
                query.edit_message_text(text=data[1] + " closed.".format(query.data))
                im.execute("UPDATE pins SET state = '"+stt+"' WHERE id='"+str(id)+"'")
            except Exception as e:
                print("GPIO Set Error")
                query.edit_message_text("Something went wrong.".format(query.data))
        try:
            im.execute("UPDATE pins SET state = '"+stt+"' WHERE id='"+str(id)+"'")
        except Exception as e:
            print("Save Database Error ! ")
        db.commit()
        db.close()
            
    
    def readPins(self):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("SELECT * FROM pins")
        data = im.fetchall()
        db.close()
        try:
            GPIO.setwarnings(False)
            GPIO.cleanup()
            GPIO.setmode(GPIO.BOARD)
            for i in data:
                GPIO.setup(int(i[0]), GPIO.OUT)
                if (i[2] == 'T'):
                    GPIO.output(int(i[0]), GPIO.HIGH)
                else:
                    GPIO.output(int(i[0]), GPIO.LOW)
        except Exception  as e:
            print(e)
        return data

    def pinKeyboardUpdate(self,id):
        i_counter = 0
        pin_temp = []
        self.pins = []
        dpin  = self.readPins()
        for pin in dpin:
            pin_temp = pin_temp + [InlineKeyboardButton(pin[1], callback_data= str(id) +"#"+pin[0])]
            i_counter += 1
            if i_counter == 3:
                self.pins = self.pins + [pin_temp]
                pin_temp = []
                i_counter = 0
            elif pin == dpin[-1]:
                self.pins = self.pins + [pin_temp]
                pin_temp = []
                i_counter = 0
    
    def userKeyboardUpdate(self,id):
        i_counter = 0
        pin_temp = []
        self.users = []
        dpin  = self.readUsers()
        for pin in dpin:
            pin_temp = pin_temp + [InlineKeyboardButton(pin[1] +" / "+ pin[0], callback_data= str(id) +"#"+pin[0])]
            i_counter += 1
            if i_counter == 2:
                self.users = self.users + [pin_temp]
                pin_temp = []
                i_counter = 0
            elif pin == dpin[-1]:
                self.users = self.users + [pin_temp]
                pin_temp = []
                i_counter = 0

    def start(self,update, context):
        if self.login(update, context):
            self.pinKeyboardUpdate(1)
            keyboard = self.pins
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                'Please choose:', reply_markup=reply_markup)

    def emsg(self,update, context):
        if self.login(update, context):
            msg = update.message.text
            if len(msg) == 1:
                self.pinKeyboardUpdate(1)
                keyboard = self.pins
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(
                    'Please choose:', reply_markup=reply_markup)

    def login(self,update, context):
        if self.isLogin(update.effective_chat.id):
            return True
        elif self.password == update.message.text:
            self.saveUser(update.effective_chat.id,"-")
            update.message.reply_text("Login Succesfully")
            return True
        else:
            update.message.reply_text("Wrong Password")
            update.message.reply_text("Try Again")
            return False

    def button(self,update, context):
        if self.login(update, context):
            query = update.callback_query
            query.answer() # str(query.data)
            aa = query.data.split("#")
            if (aa[0] == "1"):
                self.updatePinState(aa[1],query)
            elif (aa[0] == "2"):
                self.deletePin(aa[1],query)
            elif (aa[0] == "3"):
                self.deleteUser(aa[1],query)

    def help_command(self,update, context):
        update.message.reply_text("Creator: Alpaslan Tetik\nhttps://t.me/raspauto")

    def commands(self,update, context):
        update.message.reply_text("https://github.com/aattk/raspauto#telegram-bot-commands")

    def restart(self,update, context):
        if self.login(update, context):
            try:
                GPIO.cleanup()
                update.message.reply_text("Reboot Now")
                os.system("reboot")
            except Exception as e:
                print("All Pins Cleaned.")

    def temp(self,update, context):
        if self.login(update, context):
            try:
                data = subprocess.check_output('/opt/vc/bin/vcgencmd measure_temp', shell=True)
                update.message.reply_text(str(data)[2:13])
            except Exception as e:
                print("Error temp Function")
                update.message.reply_text("Temp Error")

    def libupdate(self,update, context):
        if self.login(update, context):
            try:
                direct_output = subprocess.check_output('pip3 install raspauto --upgrade', shell=True)
                update.message.reply_text(direct_output.decode('utf-8'))
                update.message.reply_text("Please Reboot /restart")
            except Exception as e:
                print("Error Update Function")
                update.message.reply_text("Something went wrong.")

    def pinadd(self,update, context):
        if self.login(update, context):
            if self.savePin(update.message.text):
                update.message.reply_text("Successfully added")
            else:
                update.message.reply_text("Something went wrong.")
                update.message.reply_text("Example Usage:")
                update.message.reply_text("/pinadd kitchen 12")

    def code(self,update, context):
        if self.login(update, context):
            cd = update.message.text
            cd = cd[6:]
            try:
                data = subprocess.check_output(str(cd), shell=True)
                update.message.reply_text(data.decode('utf-8'))
            except Exception as e:
                print("Code Run Error")
                update.message.reply_text("Code Run Error")

    def pin_list(self,update, context):
        if self.login(update, context):
            data = ""
            for i in self.readPins():
                data = data +"Name           : " + i[1] + "\nPin Number : "+ i[0] + "\n-----------------------------------------\n" 
            update.message.reply_text("# Defined Pin List\n-----------------------------------------\n"+data)
    
    def userList(self,update, context):
        if self.login(update, context):
            data = ""
            for i in self.readUsers():
                data = data +"Name             : " + i[1] + "\nUser Number : "+ i[0] + "\n-----------------------------------------\n" 
            update.message.reply_text("# User List\n-----------------------------------------\n"+data)

    def pinDelete(self,update, context):
        if self.login(update, context):
            self.pinKeyboardUpdate(2)
            keyboard = self.pins
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Please choose:', reply_markup=reply_markup)
            update.message.reply_text("Select the pin to do the deletion.")

    def user_delete(self,update, context):
        if self.login(update, context):
            self.userKeyboardUpdate(3)
            keyboard = self.users
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Please choose:', reply_markup=reply_markup)
            update.message.reply_text("Select the user to do the deletion.")
    
    def rename(self,update, context):
        if self.login(update,context):
            self.renameUser(update.effective_chat.id,update.message.text.split(" ")[1])
            update.message.reply_text("Renaming is successful.")

    def photo(self,update, context):
        if self.login(update, context):
            with picamera.PiCamera() as camera:
                camera.start_preview()
                time.sleep(4)
                camera.capture('raspauto.jpg')
                camera.stop_preview()
            time.sleep(2)
            update.message.reply_photo(photo=open('raspauto.jpg', 'rb'), timeout=240)
    
    def alarmstart(self,update,context):
        self.alarm = True
        self.alarmpeople = update
        Thread(target = self.peopleTracer).start()

    def alarmstop(self,update,context):
        self.alarm = False

    def alwayswatch(self,update,context):
        self.awatch = ~self.awatch
        self.aupdate = update;
        self.acontext = context;        
        self.alwaysphoto(self.aupdate,self.acontext)
        update.message.reply_text(f"Always Watch {self.awatch}")

    def alwaysphoto(self,update,context):
        try:
            while self.awatch:  
                self.photo(self.aupdate,self.acontext)
                print("Fotograf Gonderildi.")
        except Exception as e:
            print(f"Bir hata olsutu. {e}")