# Raspauto
### Remote management for smart technologies

![PyPI](https://img.shields.io/pypi/v/raspauto) ![PyPI - Downloads](https://img.shields.io/pypi/dm/raspauto) ![GitHub issues](https://img.shields.io/github/issues-raw/aattk/raspauto) ![GitHub](https://img.shields.io/github/license/aattk/raspauto)

### You can access and control the pins and settings of your raspberry online.


## Contents
- [**Creating a Telegram Bot**](#creating-a-telegram-bot)
- [**How to Install ?**](#how-to-install)
- [**Telegram Bot Commands**](#Telegram-Bot-Commands)

## Creating a Telegram Bot

To create our own bot account, we need to start talking to the BotFather bot. Click on the BotFather link, then after pressing the ``START`` button you will start talking. You will be greeted by the BotFather's help message. You can create your own bot by reading this message.
After sending the ``/newbot`` command as a message, it will ask for the name of the bot. Right now we'll name it My Telegram Bot. You can give any name you want. It will then ask you for a username for your telegram bot. There are only 2 terms. It ends with either ``Bot or _bot``. For example, usernames such as ``MyTelegramBot``, ``mytelegram_bot`` should be used.

After choosing a username, BotFather will send you a message containing your bot's telegram ``url`` and ``token`` value. If you want, you can change or add features to your bot. By sending the ``/help`` command as a message, BotFather will send the message that helps you what you can do.


## How to install?
This library works with Python 3. Please Install Python3.

``sudo apt-get install python3``

Let's load the Raspauto library using pip.

``sudo pip3 install raspauto``

Create a python file and write the code at the bottom

``` python
import raspauto
ra = raspauto.set("telegram_bot_token","bot_password")
ra.start()
```
**Bot Password** : You set the secret password for bot usage.

**Remember**     : You must send the password you set for the first use in plain text.
## Telegram Bot Commands
|Command|Function|Usage|
|-|-|-|
|Every key press|It sends the defined pin lists as a button.|-|
|/start|It sends the defined pin lists as a button.|``/start``|
|/pinadd|Adds pin information to the system|``/pinadd pin_name pin_number``|
|/pinlist|It shows the pin information attached to the system.|``/pinlist``|
|/pindelete|Deletes all registered pins|``/pindelete``|
|/userdelete|Deletes all registered users|``/userdelete``|
|/pinset|It is used to set up timed messages from Telegram.|``/pinset pin_number T/F``|
|/photo|Takes and sends photos.|``/photo``|
|/help|Defined functions|``/help``|
||||


