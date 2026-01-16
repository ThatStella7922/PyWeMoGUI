# PyWeMoGUI
it is a gui yes

Quick and dirty readme while I finish things up

### Requirements
- Computer with Wi-Fi
- A relatively recent Python with Tk, I used 3.12.
- A relatively recent OS, I used Windows
- Optional: OpenSSL installed and usable as `openssl` from the commandline
  - Allows setting up WeMos with password protected Wi-Fi networks

## Setup
1. Create a venv if you want
2. Install pywemo - pip should install its dependencies (requests, ifaddr, lxml, urllib3)
3. Optional: Install OpenSSL and make sure it's usable as `openssl` from the commandline. On Windows this might require editing your PATH.

## Usage
- Run python: `python3 main.py`
- After a few seconds the main window should open and say "Autodiscovery in progress" in the list.
- After autodiscovery completes, you can see the name, type and IP address of any detected WeMos on your network.

<img width=500 src=images/mainwindow.png>

There are some tabs:
- Controls lets you test a device by toggling its state (useful for lights)
- Utilities lets you rescan devices and has a help button that links to this page
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