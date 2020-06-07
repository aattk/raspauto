# RaspAuto
### Remote management for smart technologies

![PyPI](https://img.shields.io/pypi/v/raspauto) ![PyPI - Downloads](https://img.shields.io/pypi/dm/raspauto) ![GitHub issues](https://img.shields.io/github/issues-raw/aattk/raspauto) ![GitHub](https://img.shields.io/github/license/aattk/raspauto)

### You can access and control the pins and settings of your raspberry online.


## Contents
- [**How to Install ?**](#how-to-install)
- [**Firebase Registration and Project creation**](#firebase-registration-and-project-creation)
- [**Functions**](#functions)
- [**Websites**](#websites)


## How to install?
This library works with Python 3. Please Install Python3.

``sudo apt-get install python3``

Let's load the Raspauto library using pip.

``sudo pip3 install raspauto``

Create a python file and import RaspAuto.

``import raspauto as rasp``

## Firebase Registration and Project creation 
Soon... 

## Functions
``ra = rasp.set(Firebase Id,Firebase Secret Key,Device Name)``

We add our own firebase information and throw it into the ra object. After that, we will do all the functions on the ra object. You can give the name you want.

``ra.auto()``

It takes all pins assigned to this system and assigns them to raspberry pins. It performs the necessary reading and operations.

``ra.setpin(pin_id,value)``

You can assign the required value to any pin with the setpin Method. You can give the value h (High) or l (Low).

``ra.readpin(pin_id)``

You can read the value of any pin with the ReadPin Method.

## Websites