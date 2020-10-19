# -*- coding: utf-8 -*-
import time
import os
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
                update.message.reply_text("- Lutfen islem yapmak için giris yapiniz.\n\n - Giris yapmak için daha önceden olusturduGunuz sifreyi duz metin olarak mesaj atiniz.")
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
                           
                            query.edit_message_text(text=pin_edit[0] + " Kapandi".format(query.data))
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
            update.message.reply_text("Use /start to test this bot.")
        def restart(update, context):
            if login(update,context):
                self.read_pin()
                try:
                    GPIO.cleanup()
                except Exception as e:
                    print("All Pins Clean !")
                update.message.reply_text("Yeniden Baslatildi.\nAll Pins Clean !")
        def pin_add(update,context):
            if login(update,context):
                data = update.message.text.split(" ")
                update.message.reply_text(data[1]+" "+data[2]+" "+data[3])
                with open("pin.txt","a",encoding="utf-8") as file:
                    file.seek(0)
                    file.write(data[1]+" "+data[2]+" "+data[3]+"\n")
        
        def pin_list(update,context):
            if login(update,context):
                with open("pin.txt","r",encoding= "utf-8") as file:
                    dosya = file.read()
                    update.message.reply_text("--- Pin Bilgileri ---\n"+dosya)
        
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
                # camera = picamera.PiCamera()
                # camera.start_preview()
                # time.sleep(3) # hang for preview for 5 seconds
                # camera.capture('raspauto.jpg')
                # camera.stop_preview()
                with picamera.PiCamera() as camera:
                    camera.start_preview()
                    time.sleep(2)
                    camera.capture('raspauto.jpg')
                    camera.stop_preview()
                time.sleep(3)
                update.message.reply_photo(photo=open('raspauto.jpg','rb'))   

        updater = Updater(self.tid, use_context=True)
        updater.dispatcher.add_handler(CommandHandler('start', start))
        updater.dispatcher.add_handler(CommandHandler('pinadd', pin_add))
        updater.dispatcher.add_handler(CommandHandler('pinlist', pin_list))
        updater.dispatcher.add_handler(CommandHandler('pindelete', pin_delete))
        updater.dispatcher.add_handler(CommandHandler('userdelete', user_delete))
        updater.dispatcher.add_handler(CommandHandler('restart', restart))
        updater.dispatcher.add_handler(CommandHandler('photo', photo))
        updater.dispatcher.add_handler(CallbackQueryHandler(button))
        updater.dispatcher.add_handler(CommandHandler('help', help_command))
        updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, start))
        updater.start_polling()
        updater.idle()
