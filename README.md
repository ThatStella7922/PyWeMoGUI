# PyWeMoGUI
A simple GUI that lets you manage your Belkin WeMo devices.

## Overview
PyWeMoGUI lets you control, setup*, and reset any supported Belkin WeMo devices over the local network. This is useful, for example, to get your WeMos onto your home Wi-Fi network in order to use them with Home Assistant.\
<sub>* Requires a computer with Wi-Fi</sub>\
<br>
PyWeMoGUI does not require an internet connection to get your WeMos up and running, and will continue to work after Belkin shuts down the WeMo online services and app.

This README and project is not final, it will improve with time but I wanted to get this project out with the upcoming WeMo server shutdown. At the very minimum I want to release easy-to-run binaries soon.

### Requirements
- Computer with Wi-Fi
- A relatively recent Python with Tk, I used 3.12.
- A relatively recent OS, I used Windows
- Optional: OpenSSL installed and usable as `openssl` from the commandline
  - Allows setting up WeMos with password protected Wi-Fi networks

## Setup

**These instructions will be different once there are packaged binary releases available!**
- Download the repo as a zip file, or clone it. If you download a zip, extract it to a folder.
- Create a venv if you want to keep this self-contained
    - `python3 -m venv venv` to create it
    - `venv\scripts\activate` to enter it
- Install pywemo - pip should install its dependencies (requests, ifaddr, lxml, urllib3)
    - `pip3 install pywemo`
- Optional: Install OpenSSL and make sure it's usable as `openssl` from the commandline. On Windows this might require editing your PATH.

## Usage
- Run python: `python3 main.py`
- After a few seconds the main window should open and say "Autodiscovery in progress" in the list.

<img width=500 src=images/mainwindow.png>

After autodiscovery completes, any WeMos on your network will show up in the list. It'll show the name of the device, the type, and its IP address. You can click on a device in the list to select it.

There are some tabs:
- Controls lets you test a device by toggling its state (useful for lights)
- Utilities lets you rescan the device list and has a help button that links to this page
- Setup WeMo contains everything required to setup a WeMo that has been reset, more on this later
- Reset WeMo lets you reset a WeMo's personalized info, Wi-Fi settings or even fully factory reset it.

### Setting up a WeMo
To set up a WeMo, it has to be factory reset - or at the very least have had its Wi-Fi settings reset. You can reset it with PyWeMoGUI or on the WeMo itself, usually with some button combination.

1. Plug it in/turn it on and wait for it to start up
2. Search for a WeMo Wi-Fi network nearby, something like "Wemo.Dim2G"
3. Connect to the WeMo network, it should have no password
4. Open PyWeMoGUI or rescan devices if it's already open
5. You should see a single device in the table with the factory name of your device. For example a Dimmer will be named "Wemo Dimmer" in the list. Select it.
6. Navigate to the Setup WeMo tab, then enter the details of the Wi-Fi network you want the WeMo to connect to. If it has no password, check the 'No password/Open network' checkbox
> [!NOTE]  
> Remember that you need OpenSSL usable from the commandline if you want to connect the WeMo to a password-protected network!
7. If all goes well, your WeMo should reboot a few seconds later to apply its new settings

### Resetting a WeMo
Select the WeMo you want to reset in the list, click the appropriate button for the reset you want to perform, then click Yes in the confirmation box. The WeMo will restart after a few seconds to clear its settings.

## Attribution and license
All rights are **not** reserved. https://github.com/pywemo and https://github.com/iancmcc/ouimeaux are not my code and those belong to their respective authors. The PyWeMoGUI code is licensed under the GPLv3.
