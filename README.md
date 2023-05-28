# Raspauto
### Remote management for smart technologies

![PyPI](https://img.shields.io/pypi/v/raspauto) ![PyPI - Downloads](https://img.shields.io/pypi/dm/raspauto) ![GitHub issues](https://img.shields.io/github/issues-raw/aattk/raspauto) ![GitHub](https://img.shields.io/github/license/aattk/raspauto) ![Lines of code](https://img.shields.io/tokei/lines/github/aattk/raspauto) ![GitHub last commit](https://img.shields.io/github/last-commit/aattk/raspauto) 

### You can access and control the pins and settings of your raspberry online.
- You can talk to me on [Telegram](https://t.me/raspauto). 
- Use [Telegram](https://t.me/raspauto) for ideas.
- Please use ["Github Issues"](https://github.com/aattk/raspauto/issues) to report bugs.


## Contents
- [**Creating a Telegram Bot**](#creating-a-telegram-bot)
- [**How to Install ?**](#how-to-install)
- [**How to add it to the beginning?**](#startup)
- [**Telegram Bot Commands**](#Telegram-Bot-Commands)


## Creating a Telegram Bot

To create our own bot account, we need to start talking to the BotFather bot. Click on the [BotFather](https://telegram.me/botfather) link, then after pressing the ``START`` button you will start talking. You will be greeted by the [BotFather](https://telegram.me/botfather)'s help message. You can create your own bot by reading this message.
After sending the ``/newbot`` command as a message, it will ask for the name of the bot. Right now we'll name it My Telegram Bot. You can give any name you want. It will then ask you for a username for your telegram bot. There are only 2 terms. It ends with either ``Bot or _bot``. For example, usernames such as ``MyTelegramBot``, ``mytelegram_bot`` should be used.

After choosing a username, BotFather will send you a message containing your bot's telegram ``url`` and ``token`` value. If you want, you can change or add features to your bot. By sending the ``/help`` command as a message, BotFather will send the message that helps you what you can do.


## How to install?
This library works with Python 3. Please Install Python3.

``` 
sudo apt-get install python3 
```

Let's load the Raspauto library using pip.

```
sudo pip3 install raspauto
```

Create a python file and write the code at the bottom

``` python
import raspauto as ra
ra.set("telegram_bot_token","bot_password")
```
**Bot Password** : You set the secret password for bot usage.

**Remember**     : You must send the password you set for the first use in plain text.

If there is an error in activating or deactivating the button, please give permission to write to the database with the help of the command at the bottom.

```
sudo chmod 777 ra.sqlite
```

## How to add it to the beginning?
Download service file.

```
wget https://raw.githubusercontent.com/aattk/raspauto/master/demo/ra.service
```

Perform the copy operation to add to the beginning.

```
sudo cp ra.service /etc/systemd/system/ra.service
```

The python file name must be ``ra.py`` for this process to work. Also, the ``ra.py`` file should be under the folder ``/home/pi``. If you want to change it yourself. You can look at the sample service file under the demo folder.

We activate the service.

```
sudo systemctl enable ra.service
```

We start the operation of the system by rebooting.

```
sudo reboot
```

## Telegram Bot Commands
|Command|Function|Usage|
|-|-|-|
|Every key press|It sends the defined pin lists as a button.|-|
|/login|Allows the user to log in.|``/login your_password``|
|/start|It sends the defined pin lists as a button.|``/start``|
|/pinadd|Adds pin information to the system|``/pinadd pin_name pin_number``|
|/pinlist|It shows the pin information attached to the system.|``/pinlist``|
|/userlist|It shows the user information attached to the system.|``/userlist``|
|/pindelete|Starts the Pin Delete process.|``/pindelete``|
|/userdelete|Starts the User Delete process.|``/userdelete``|
|/rename|Used to name the user.|``/rename name``|
|/photo|Takes and sends photos.|``/photo``|
|/help|Defined functions|``/help``|
|/temp|Give Temp|``/temp``|
|/restart|Restart Raspberry|``/restart``|
|/libupdate|Update Raspauto and Reboot|``/libupdate``|
|/code|You use it to execute code|``/code your_code``|
|/commands|Defined command list|``/commands``|
||||

## Version List
#### version 0.2.2.x 18/05/2021 22:26
- Database has been used.
- Pin and user deletion has been updated.
- The /pinset command has been removed. Development continues for the new command.
- Minor bugs fixed.

#### version 0.2.0.2
- You can now run Code with Bot. / code
- Replying to every message has been removed. instead it started responding to a single letter, number or /start commands. 
- /commands Function has been edited
- Minor Bugs fixed.
- Restart Function Fixed.
#### version 0.2.0.1
- Minor Bugs fixed.
#### version 0.1.9.9
- Library Update Function Added.
#### version 0.1.8.9
- Temp Function Added.
#### version 0.1.8.8
- Restart Command is RUN.
#### version 0.1.8.6
- The descriptions have been created.
#### version 0.1.8.5
- Camera support added 
#### version 0.1.8.0
- Telegram Button Usage Added.
- Adding users via Telegram 
- User delete via Telegram 
- Added adding pin via Telegram
- Added delete pin via Telegram
#### version 0.1.6.5
- Firebase support has been replaced by Telegram.
