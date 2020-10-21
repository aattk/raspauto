# Raspauto
### Remote management for smart technologies

![PyPI](https://img.shields.io/pypi/v/raspauto) ![PyPI - Downloads](https://img.shields.io/pypi/dm/raspauto) ![GitHub issues](https://img.shields.io/github/issues-raw/aattk/raspauto) ![GitHub](https://img.shields.io/github/license/aattk/raspauto)

### You can access and control the pins and settings of your raspberry online.


## Contents
- [**How to Install ?**](#how-to-install)
- [**Creating a Telegram Bot**](#how-to-install)

## Creating a Telegram Bot


## How to install?
This library works with Python 3. Please Install Python3.

``sudo apt-get install python3``

Let's load the Raspauto library using pip.

``sudo pip3 install raspauto``

Create a python file and import RaspAuto.

``import raspauto as rasp``

## Sample Code

``` python
import raspauto
ra = raspauto.set("telegram_bot_secret_key","bot_password")
ra.start()
```
``Bot Password : You set the secret password for bot usage``

## Telegram Bot Commands
|Command|Function|Usage|
|-|-|-|
|Every key press|It sends the defined pin lists as a button.|-|
|/start|||
|/pinadd|||
|/pinlist|||
|/pindelete|||


