# -*- coding: utf-8 -*-
import time
import os
import subprocess
from threading import Thread
import telegram
import cv2
import sqlite3 as sql

try:
    import RPi.GPIO as GPIO
    import picamera
except Exception as e:
    print("GPIO kütüphanesi bulunamadı")

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters


class set:
    def __init__(self, telegram_id, password):
        self.tid = telegram_id
        self.password = password
        self.pins = []
        self.dbinit()
        self.pinKeyboardUpdate(1)

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
        if (data[2] == 'F'):
            stt = "T"
            try:
                query.edit_message_text(text=data[1] + " opened.".format(query.data))
                GPIO.output(int(data[0]), 0)
            except Exception as e:
                query.edit_message_text("Something went wrong.".format(query.data))
        else: 
            stt = "F"
            try:
                query.edit_message_text(text=data[1] + " closed.".format(query.data))
                GPIO.output(int(data[0]), 0)
            except Exception as e:
                query.edit_message_text("Something went wrong.".format(query.data))
        im.execute("UPDATE pins SET state = '"+stt+"' WHERE id='"+str(id)+"'")
        db.commit()
        db.close()
            
    
    def readPins(self):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("SELECT * FROM pins")
        data = im.fetchall()
        db.close()
        try:
            GPIO.cleanup()
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            for i in data:
                GPIO.setup(int(i[0]), GPIO.OUT)
                if (i[2] == 'T'):
                    GPIO.output(int(i[0]), GPIO.HIGH)
                else:
                    GPIO.output(i, GPIO.LOW)
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

    def peopleTracer(self):
        while self.alarm:
            print("Alpaslan")
            time.sleep(1)

    def start(self):
        def start(update, context):
            if login(update, context):
                self.pinKeyboardUpdate(1)
                keyboard = self.pins
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(
                    'Please choose:', reply_markup=reply_markup)

        def emsg(update, context):
            if login(update, context):
                msg = update.message.text
                if len(msg) == 1:
                    self.pinKeyboardUpdate(1)
                    keyboard = self.pins
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_text(
                        'Please choose:', reply_markup=reply_markup)

        def login(update, context):
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

        def button(update, context):
            if login(update, context):
                query = update.callback_query
                query.answer() # str(query.data)
                aa = query.data.split("#")
                if (aa[0] == "1"):
                    self.updatePinState(aa[1],query)
                elif (aa[0] == "2"):
                    self.deletePin(aa[1],query)
                elif (aa[0] == "3"):
                    self.deleteUser(aa[1],query)

        def help_command(update, context):
            update.message.reply_text("Creator: Alpaslan Tetik\nhttps://t.me/raspauto")

        def commands(update, context):
            update.message.reply_text("https://github.com/aattk/raspauto#telegram-bot-commands")

        def restart(update, context):
            if login(update, context):
                try:
                    GPIO.cleanup()
                    update.message.reply_text("Reboot Now")
                    os.system("reboot")
                except Exception as e:
                    print("All Pins Cleaned.")

        def temp(update, context):
            if login(update, context):
                try:
                    data = subprocess.check_output('/opt/vc/bin/vcgencmd measure_temp', shell=True)
                    update.message.reply_text(str(data)[2:13])
                except Exception as e:
                    print("Error temp Function")
                    update.message.reply_text("Temp Error")

        def libupdate(update, context):
            if login(update, context):
                try:
                    direct_output = subprocess.check_output('pip3 install raspauto --upgrade', shell=True)
                    update.message.reply_text(direct_output.decode('utf-8'))
                    update.message.reply_text("Please Reboot /restart")
                except Exception as e:
                    print("Error Update Function")
                    update.message.reply_text("Something went wrong.")

        def pinadd(update, context):
            if login(update, context):
                if self.savePin(update.message.text):
                    update.message.reply_text("Successfully added")
                else:
                    update.message.reply_text("Something went wrong.")
                    update.message.reply_text("Example Usage:")
                    update.message.reply_text("/pinadd kitchen 12")

        def code(update, context):
            if login(update, context):
                cd = update.message.text
                cd = cd[6:]
                try:
                    data = subprocess.check_output(str(cd), shell=True)
                    update.message.reply_text(data.decode('utf-8'))
                except Exception as e:
                    print("Code Run Error")
                    update.message.reply_text("Code Run Error")

        def pin_list(update, context):
            if login(update, context):
                data = ""
                for i in self.readPins():
                    data = data +"Name           : " + i[1] + "\nPin Number : "+ i[0] + "\n-----------------------------------------\n" 
                update.message.reply_text("# Defined Pin List\n-----------------------------------------\n"+data)
        
        def userList(update, context):
            if login(update, context):
                data = ""
                for i in self.readUsers():
                    data = data +"Name             : " + i[1] + "\nUser Number : "+ i[0] + "\n-----------------------------------------\n" 
                update.message.reply_text("# User List\n-----------------------------------------\n"+data)

        def pinDelete(update, context):
            if login(update, context):
                self.pinKeyboardUpdate(2)
                keyboard = self.pins
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text('Please choose:', reply_markup=reply_markup)
                update.message.reply_text("Select the pin to do the deletion.")

        def user_delete(update, context):
            if login(update, context):
                self.userKeyboardUpdate(3)
                keyboard = self.users
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text('Please choose:', reply_markup=reply_markup)
                update.message.reply_text("Select the user to do the deletion.")
        
        def rename(update, context):
            if login(update,context):
                self.renameUser(update.effective_chat.id,update.message.text.split(" ")[1])
                update.message.reply_text("Renaming is successful.")

        def photo(update, context):
            if login(update, context):
                with picamera.PiCamera() as camera:
                    camera.start_preview()
                    time.sleep(4)
                    camera.capture('raspauto.jpg')
                    camera.stop_preview()
                time.sleep(2)
                update.message.reply_photo(photo=open('raspauto.jpg', 'rb'), timeout=240)
        
        def alarmstart(update,context):
            self.alarm = True
            self.alarmpeople = update.effective_chat.id
            Thread(target = self.peopleTracer).start()

        def alarmstop(update,context):
            self.alarm = False



        updater = Updater(self.tid, use_context=True)
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(CommandHandler('pinadd', pinadd))
        updater.dispatcher.add_handler(CommandHandler('pinlist', pin_list))
        updater.dispatcher.add_handler(CommandHandler('pindelete', pinDelete))
        updater.dispatcher.add_handler(CommandHandler('userdelete', user_delete))
        updater.dispatcher.add_handler(CommandHandler('userlist', userList))
        updater.dispatcher.add_handler(CommandHandler('rename', rename))
        # updater.dispatcher.add_handler(CommandHandler('pinset', pinset))
        updater.dispatcher.add_handler(CommandHandler('restart', restart))
        updater.dispatcher.add_handler(CommandHandler('photo', photo))
        updater.dispatcher.add_handler(CommandHandler('alarmstart', alarmstart))
        updater.dispatcher.add_handler(CommandHandler('alarmstop', alarmstop))
        updater.dispatcher.add_handler(CommandHandler('temp', temp))
        updater.dispatcher.add_handler(CommandHandler('code', code))
        updater.dispatcher.add_handler(CommandHandler('commands', commands))
        updater.dispatcher.add_handler(CommandHandler('libupdate', libupdate))
        updater.dispatcher.add_handler(CallbackQueryHandler(button))
        updater.dispatcher.add_handler(CommandHandler('help', help_command))
        updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, emsg))
        updater.start_polling()
        updater.idle()