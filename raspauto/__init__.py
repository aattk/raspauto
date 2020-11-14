# -*- coding: utf-8 -*-
import time
import os
import subprocess
import telegram
try:
    import RPi.GPIO as GPIO
    import picamera
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
except Exception as e:
    print("GPIO kütüphanesi bulunamadı")

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler,Filters

class set:
    def __init__(self,telegram_id,password):
        self.tid = telegram_id
        self.password = password
        self.pins = []
        self.read_pin()
    def read_pin(self):
        print("Yapilandirma ayarlari yukleniyor.")
        self.pins = [] 
        try:
            with open("pin.txt","r",encoding="utf-8") as file:
                self.inst = file.readlines()
            self.re_built_list()
            print("Yapilandirma ayarlari yuklendi.")
        except Exception as e:
            print("Yapılandırma Dosyaları Bulunamadı.")
            self.build_file()
        
    def build_file(self):
        file = open("pin.txt","a",encoding="utf-8")
        file.close()
        file2 = open("user.txt","a",encoding="utf-8")
        file2.close()
        self.read_pin()
    def re_built_list(self):
        i_counter = 0
        pin_temp = []
        for i in self.inst:
            pin = i.replace("\n","").split(" ")
            try:
                # GPIO kısmı 
                GPIO.setup(int(pin[1]), GPIO.OUT)
                # GPIO Bitiş
            except Exception as e:
                print(f"Hata oluştu {e}")
            
            pin_temp = pin_temp  + [InlineKeyboardButton(pin[0], callback_data=pin[1])]
            i_counter += 1
            if i_counter == 3:
                self.pins = self.pins + [pin_temp]
                pin_temp = []
                i_counter = 0
            elif i == self.inst[-1]:
                self.pins = self.pins + [pin_temp]
                pin_temp = []
                i_counter = 0
    def start(self):
        def start(update, context):
            if  login(update,context):
                keyboard = self.pins
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text('Please choose:', reply_markup=reply_markup)

        def emsg(update, context):
            if  login(update,context):
                msg = update.message.text
                if len(msg) == 1:
                    keyboard = self.pins
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_text('Please choose:', reply_markup=reply_markup)

        def login(update, context):
            with open("user.txt","r",encoding="utf-8") as file:
                self.users = file.readlines()
            if str(update.effective_chat.id)+"\n" in self.users:
                return True
            elif self.password == update.message.text:
                with open("user.txt","a",encoding="utf-8") as file:
                    file.seek(0)
                    file.write(str(update.effective_chat.id)+"\n")
                    update.message.reply_text("Giris Basarili.")
                    return True
            else:
                update.message.reply_text("Please Send Password : ")
                return False
        def button(update, context):
            if login(update,context):
                query = update.callback_query
                query.answer()
                with open("pin.txt","r",encoding="utf-8") as file:
                    pins = file.readlines()
                new_pins = []
                for i in pins:
                    pin_edit = i.replace("\n","").split(" ")
                    if str(pin_edit[1]) == str(query.data):
                        if str(pin_edit[2]) == str("T") :
                            new_pin = str(pin_edit[0]) +" "+ str(pin_edit[1]) +" F\n"
                            new_pins = new_pins + [new_pin]
                            try:
                                 # GPIO Değer değiştirme
                                GPIO.output(int(pin_edit[1]),0)
                            except Exception as e:
                                print("Error GPIO set")
                           
                            query.edit_message_text(text=pin_edit[0] + " Closed".format(query.data))
                        elif str(pin_edit[2]) == str("F") :
                            new_pin = str(pin_edit[0]) +" "+ str(pin_edit[1]) +" T\n"
                            new_pins = new_pins + [new_pin]
                            try:
                                 # GPIO Değer değiştirme
                                GPIO.output(int(pin_edit[1]),1)
                            except Exception as e:
                                print("Error GPIO set")
                            query.edit_message_text(text=pin_edit[0]+ " Açildi".format(query.data))
                    else:
                        new_pins = new_pins + [str(i)]
                with open("pin.txt","w",encoding = "utf-8") as file:
                    file.writelines(new_pins)
            
        def help_command(update, context):
            update.message.reply_text("Creator: Alpaslan Tetik\nhttps://t.me/raspauto")
        def commands(update, context):
            update.message.reply_text("/start .\n/photo \n ")
        def restart(update, context):
            if login(update,context):
                self.read_pin()
                try:
                    GPIO.cleanup()
                    os.system("reboot")
                except Exception as e:
                    print("All Pins Clean !")
                update.message.reply_text("Yeniden Baslatiliyor.")
        def temp(update, context):
            if login(update,context):
                try:
                    data = subprocess.check_output('/opt/vc/bin/vcgencmd measure_temp', shell=True)
                    update.message.reply_text(str(data)[2:13])
                except Exception as e:
                    print("Error temp Function")
                    update.message.reply_text("Temp Error")
        
        def libupdate(update, context):
            if login(update,context):
                try:
                    direct_output = subprocess.check_output('pip3 install raspauto --upgrade', shell=True)
                    update.message.reply_text(direct_output.decode('utf-8'))
                    update.message.reply_text("Please Reboot /restart")
                except Exception as e:
                    print("Error Update Function")
                    update.message.reply_text("Error Update Function")

                
        def pin_add(update,context):
            if login(update,context):
                data = update.message.text.split(" ")
                update.message.reply_text(data[1]+" "+data[2]+" "+data[3])
                with open("pin.txt","a",encoding="utf-8") as file:
                    file.seek(0)
                    file.write(data[1]+" "+data[2]+" "+data[3]+"\n")
        def code(update,context):
            if login(update,context):
                cd = update.message.text
                cd = cd[6:]
                try:
                    data = subprocess.check_output(str(cd), shell=True)
                    update.message.reply_text(data.decode('utf-8'))
                except Exception as e:
                    print("Code Run Error")
                    update.message.reply_text("Code Run Error")
        def pinset(update,context):
            if login(update,context):
                data = update.message.text.split(" ")
                with open("pin.txt","r",encoding="utf-8") as file:
                    pins = file.readlines()
                new_pins = []
                for i in pins:
                    pin_edit = i.replace("\n","").split(" ")
                    if str(pin_edit[1]) == str(data[1]):
                        if str(data[2]) == str("T") :
                            new_pin = str(pin_edit[0]) +" "+ str(pin_edit[1]) +" F\n"
                            new_pins = new_pins + [new_pin]
                            try:
                                 # GPIO Değer değiştirme
                                GPIO.output(int(pin_edit[1]),0)
                            except Exception as e:
                                print("Error GPIO set")
                            update.message.reply_text("Ayarlanan pin açıldı.")
                            
                        elif str(data[2]) == str("F") :
                            new_pin = str(pin_edit[0]) +" "+ str(pin_edit[1]) +" T\n"
                            new_pins = new_pins + [new_pin]
                            try:
                                 # GPIO Değer değiştirme
                                GPIO.output(int(pin_edit[1]),1)
                            except Exception as e:
                                print("Error GPIO set")
                            update.message.reply_text("Ayarlanan pin kapatıldı.")
                    else:
                        new_pins = new_pins + [str(i)]
                with open("pin.txt","w",encoding = "utf-8") as file:
                    file.writelines(new_pins)
        
        def pin_list(update,context):
            if login(update,context):
                with open("pin.txt","r",encoding= "utf-8") as file:
                    dosya = file.read()
                    update.message.reply_text("--- Pin List ---\n"+dosya)
        
        def pin_delete(update,context):
            if login(update,context):
                with open("pin.txt","w",encoding="utf-8") as file:
                    file.write("")
                update.message.reply_text("Pinler Silindi.")
        def user_delete(update,context):
            if login(update,context):
                with open("user.txt","w",encoding="utf-8") as file:
                    file.write("")
                update.message.reply_text("Bütün Kullanıcılar Silindi")
        def photo(update,context):
            if login(update,context):
                with picamera.PiCamera() as camera:
                    camera.start_preview()
                    time.sleep(4)
                    camera.capture('raspauto.jpg')
                    camera.stop_preview()
                time.sleep(2)
                update.message.reply_photo(photo=open('raspauto.jpg','rb'),timeout = 240)   

        updater = Updater(self.tid, use_context=True)
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(CommandHandler('pinadd', pin_add))
        updater.dispatcher.add_handler(CommandHandler('pinlist', pin_list))
        updater.dispatcher.add_handler(CommandHandler('pindelete', pin_delete))
        updater.dispatcher.add_handler(CommandHandler('userdelete', user_delete))
        updater.dispatcher.add_handler(CommandHandler('pinset', pinset))
        updater.dispatcher.add_handler(CommandHandler('restart', restart))
        updater.dispatcher.add_handler(CommandHandler('photo', photo))
        updater.dispatcher.add_handler(CommandHandler('temp', temp))
        updater.dispatcher.add_handler(CommandHandler('code', code))
        updater.dispatcher.add_handler(CommandHandler('commands', commands))
        updater.dispatcher.add_handler(CommandHandler('libupdate', libupdate))
        updater.dispatcher.add_handler(CallbackQueryHandler(button))
        updater.dispatcher.add_handler(CommandHandler('help', help_command))
        updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, emsg))
        updater.start_polling()
        updater.idle()
