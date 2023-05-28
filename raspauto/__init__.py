# -*- coding: utf-8 -*-
import os
import sqlite3 as sql
import subprocess
import time
from threading import Thread

import speech_recognition as sr
from gtts import gTTS

try:
    import picamera
    import RPi.GPIO as GPIO
except Exception as e:
    print("GPIO Library not found.")


from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, filters, MessageHandler, Updater


class set:
    def __init__(self, telegram_id, password):
        self.tid = telegram_id
        self.password = password
        self.pins = []
        self.awatch = False
        self.asistan_state = True
        self.aupdate = []
        self.acontext = []
        self.loginErrortext = "You are not logged in. Please login with /login <password> command."
        self.dbinit()
        self.pinKeyboardUpdate(1)
        self.updateInit()
        self.asistan()

    def updateInit(self):
        """Run the bot."""
        # Create the Application and pass it your bot's token.
        application = Application.builder().token(self.tid).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("pinadd", self.pinadd))
        application.add_handler(CommandHandler("pinlist", self.pin_list))
        application.add_handler(CommandHandler("pindelete", self.pinDelete))
        application.add_handler(CommandHandler("userdelete", self.user_delete))
        application.add_handler(CommandHandler("userlist", self.userList))
        application.add_handler(CommandHandler("rename", self.rename))
        application.add_handler(CommandHandler("restart", self.restart))
        application.add_handler(CommandHandler("photo", self.photo))
        application.add_handler(CommandHandler("alarmstart", self.alarmstart))
        application.add_handler(CommandHandler("alarmstop", self.alarmstop))
        application.add_handler(CommandHandler("temp", self.temp))
        application.add_handler(CommandHandler("code", self.code))
        application.add_handler(CommandHandler("commands", self.commands))
        application.add_handler(CommandHandler("libupdate", self.libupdate))
        application.add_handler(CommandHandler("asistan", self.asistan))
        application.add_handler(CommandHandler("login", self.login))
        application.add_handler(CommandHandler(
            "asistan_stop", self.asistan_stop))
        application.add_handler(CommandHandler(
            "alwayswatch", self.alwayswatch))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.emsg))

        # Run the bot until the user presses Ctrl-C
        application.run_polling()

    def dbinit(self):
        if(not os.path.isfile("ra.sqlite")):
            db = sql.connect('ra.sqlite')
            im = db.cursor()
            im.execute("CREATE TABLE users (id, name)")
            im.execute("CREATE TABLE pins (id,name,state)")
            im.execute("CREATE TABLE alarm (id,state)")
            im.execute("CREATE TABLE language (lcode,data)")

    def saveUser(self, id, name):
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

    def renameUser(self, id, name):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("UPDATE users SET name = '"+name+"' WHERE id='"+str(id)+"'")
        db.commit()
        db.close()

    def isLogin(self, id):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("SELECT * FROM users where id = '"+str(id)+"'")
        data = im.fetchall()
        db.close()
        if len(data) > 0:
            return True
        else:
            return False

    def savePin(self, data):
        data = data.split(" ")
        if len(data) > 1:
            db = sql.connect('ra.sqlite')
            im = db.cursor()
            im.execute("INSERT INTO pins VALUES ('" +
                       str(data[2])+"', '"+str(data[1])+"','F')")
            db.commit()
            db.close()
            return True
        else:
            return False

    def deletePin(self, id, query):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("SELECT * FROM pins where id = '"+str(id)+"'")
        data = im.fetchone()
        im.execute("DELETE FROM pins WHERE id = '"+str(id)+"'")
        query.edit_message_text(text=data[1] + " deleted.".format(query.data))
        db.commit()
        db.close()

    def deleteUser(self, id, query):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("SELECT * FROM users where id = '"+str(id)+"'")
        data = im.fetchone()
        im.execute("DELETE FROM users WHERE id = '"+str(id)+"'")
        query.edit_message_text(text=data[1] + " deleted.".format(query.data))
        db.commit()
        db.close()

    def updatePinState(self, id, query):
        db = sql.connect('ra.sqlite')
        im = db.cursor()
        im.execute("SELECT * FROM pins where id = '"+str(id)+"'")
        data = im.fetchone()
        stt = ""
        if (data[2] == 'F'):
            stt = "T"
            try:
                GPIO.output(int(data[0]), GPIO.HIGH)
                query.edit_message_text(
                    text=data[1] + " opened.".format(query.data))
            except Exception as e:
                print("GPIO Set Error")
                query.edit_message_text(
                    "Something went wrong.".format(query.data))
        elif (data[2] == 'T'):
            stt = "F"
            try:
                GPIO.output(int(data[0]), GPIO.LOW)
                query.edit_message_text(
                    text=data[1] + " closed.".format(query.data))
                im.execute("UPDATE pins SET state = '" +
                           stt+"' WHERE id='"+str(id)+"'")
            except Exception as e:
                print("GPIO Set Error")
                query.edit_message_text(
                    "Something went wrong.".format(query.data))
        try:
            im.execute("UPDATE pins SET state = '" +
                       stt+"' WHERE id='"+str(id)+"'")
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
        except Exception as e:
            print(e)
        return data

    def pinKeyboardUpdate(self, id):
        i_counter = 0
        pin_temp = []
        self.pins = []
        dpin = self.readPins()
        for pin in dpin:
            pin_temp = pin_temp + \
                [InlineKeyboardButton(
                    pin[1], callback_data=str(id) + "#"+pin[0])]
            i_counter += 1
            if i_counter == 3:
                self.pins = self.pins + [pin_temp]
                pin_temp = []
                i_counter = 0
            elif pin == dpin[-1]:
                self.pins = self.pins + [pin_temp]
                pin_temp = []
                i_counter = 0

    def userKeyboardUpdate(self, id):
        i_counter = 0
        pin_temp = []
        self.users = []
        dpin = self.readUsers()
        for pin in dpin:
            pin_temp = pin_temp + \
                [InlineKeyboardButton(
                    pin[1] + " / " + pin[0], callback_data=str(id) + "#"+pin[0])]
            i_counter += 1
            if i_counter == 2:
                self.users = self.users + [pin_temp]
                pin_temp = []
                i_counter = 0
            elif pin == dpin[-1]:
                self.users = self.users + [pin_temp]
                pin_temp = []
                i_counter = 0

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            self.pinKeyboardUpdate(1)
            keyboard = self.pins
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                'Please choose:', reply_markup=reply_markup)
        else:
            await update.message.reply_text(self.loginErrortext)

    async def emsg(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            msg = update.message.text
            if len(msg) == 1:
                self.pinKeyboardUpdate(1)
                keyboard = self.pins
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    'Please choose:', reply_markup=reply_markup)
        else:
            await update.message.reply_text(self.loginErrortext)

    async def login(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            return True
        elif self.password == update.message.text.split(" ")[1]:
            self.saveUser(update.effective_chat.id, "-")
            await update.message.reply_text("Login Succesfully")
            return True
        else:
            await update.message.reply_text("Wrong Password")
            await update.message.reply_text("Try Again")
            return False

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            query = update.callback_query
            query.answer()  # str(query.data)
            aa = query.data.split("#")
            if (aa[0] == "1"):
                self.updatePinState(aa[1], query)
            elif (aa[0] == "2"):
                self.deletePin(aa[1], query)
            elif (aa[0] == "3"):
                self.deleteUser(aa[1], query)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Creator: Alpaslan Tetik\nhttps://t.me/raspauto")

    async def commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "https://github.com/aattk/raspauto#telegram-bot-commands")

    async def restart(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            try:
                GPIO.cleanup()
                await update.message.reply_text("Reboot Now")
                os.system("reboot")
            except Exception as e:
                print("All Pins Cleaned.")

    async def temp(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            try:
                data = subprocess.check_output(
                    '/opt/vc/bin/vcgencmd measure_temp', shell=True)
                await update.message.reply_text(str(data)[2:13])
            except Exception as e:
                print("Error temp Function")
                await update.message.reply_text("Temp Error")
        else:
            await update.message.reply_text(self.loginErrortext)

    async def libupdate(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            try:
                direct_output = subprocess.check_output(
                    'pip3 install raspauto --upgrade', shell=True)
                await update.message.reply_text(direct_output.decode('utf-8'))
                await update.message.reply_text("Please Reboot /restart")
            except Exception as e:
                print("Error Update Function")
                await update.message.reply_text("Something went wrong.")
        else:
            await update.message.reply_text(self.loginErrortext)

    async def pinadd(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            if self.savePin(update.message.text):
                await update.message.reply_text("Successfully added")
            else:
                await update.message.reply_text("Something went wrong.")
                await update.message.reply_text("Example Usage:")
                await update.message.reply_text("/pinadd kitchen 12")
        else:
            await update.message.reply_text(self.loginErrortext)

    async def code(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            cd = update.message.text
            cd = cd[6:]
            try:
                data = subprocess.check_output(str(cd), shell=True)
                update.message.reply_text(data.decode('utf-8'))
            except Exception as e:
                print("Code Run Error")
                await update.message.reply_text("Code Run Error")
        else:
            await update.message.reply_text(self.loginErrortext)

    async def pin_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            data = ""
            for i in self.readPins():
                data = data + "Name           : " + \
                    i[1] + "\nPin Number : " + i[0] + \
                    "\n-----------------------------------------\n"
            await update.message.reply_text("# Defined Pin List\n-----------------------------------------\n"+data)
        else:
            await update.message.reply_text(self.loginErrortext)

    async def userList(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            data = ""
            for i in self.readUsers():
                data = data + "Name             : " + \
                    i[1] + "\nUser Number : " + i[0] + \
                    "\n-----------------------------------------\n"
            await update.message.reply_text(
                "# User List\n-----------------------------------------\n"+data)
        else:
            await update.message.reply_text(self.loginErrortext)

    async def pinDelete(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            self.pinKeyboardUpdate(2)
            keyboard = self.pins
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                'Please choose:', reply_markup=reply_markup)
            await update.message.reply_text("Select the pin to do the deletion.")
        else:
            await update.message.reply_text(self.loginErrortext)

    async def user_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            self.userKeyboardUpdate(3)
            keyboard = self.users
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                'Please choose:', reply_markup=reply_markup)
            await update.message.reply_text("Select the user to do the deletion.")
        else:
            await update.message.reply_text(self.loginErrortext)

    async def rename(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            self.renameUser(update.effective_chat.id,
                            update.message.text.split(" ")[1])
            await update.message.reply_text("Renaming is successful.")
        else:
            await update.message.reply_text(self.loginErrortext)

    async def photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.isLogin(update.effective_chat.id):
            with picamera.PiCamera() as camera:
                camera.start_preview()
                time.sleep(4)
                camera.capture('raspauto.jpg')
                camera.stop_preview()
            time.sleep(2)
            await update.message.reply_photo(photo=open(
                'raspauto.jpg', 'rb'), timeout=240)
        else:
            await update.message.reply_text(self.loginErrortext)

    async def alarmstart(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.alarm = True
        self.alarmpeople = update
        Thread(target=self.peopleTracer).start()

    async def alarmstop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.alarm = False

    async def alwayswatch(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.awatch = ~self.awatch
        self.aupdate = update
        self.acontext = context
        self.alwaysphoto(self.aupdate, self.acontext)
        await update.message.reply_text(f"Always Watch {self.awatch}")

    async def alwaysphoto(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            while self.awatch:
                self.photo(self.aupdate, self.acontext)
                print("Fotograf Gonderildi.")
        except Exception as e:
            print(f"Bir hata olsutu. {e}")

    def speak(self, message):
        tts = gTTS(text=message, lang='tr')
        tts.save("audio.mp3")
        os.system("audio.mp3")

    def recordAudio(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)
        data = ""
        try:
            data = r.recognize_google(audio, language='tr-tr')
            data = data.lower()
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        return data

    async def asistan(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        while(self.asistan_state):
            data = self.recordAudio()
            self.komut_olustur(data)
        self.asistan_state = True

    async def asistan_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.asistan_state = False
        await update.message.reply_text(f"Assistant turned off.")

    def komut_olustur(self, data):
        for i in self.readPins():
            if i[1].lower() in data:
                if "aç" in data:
                    self.speak(f"{i[1]} açıldı.")
                elif "kapat" in data:
                    self.speak(f"{i[1]} kapatıldı.")
