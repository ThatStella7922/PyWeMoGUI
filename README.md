# PyWeMoGUI
A simple GUI that lets you manage your Belkin WeMo devices.

## Overview
PyWeMoGUI lets you control, setup*, and reset any supported Belkin WeMo devices over the local network. This is useful, for example, to get your WeMos onto your home Wi-Fi network in order to use them with Home Assistant. It also supports acquiring HomeKit setup codes from compatible WeMos, in the case that the WeMo's own HomeKit code was lost or damaged.\
<sub>* Requires a computer with Wi-Fi</sub>\
<br>
PyWeMoGUI does not require an internet connection to get your WeMos up and running thanks to the [pywemo](https://github.com/pywemo/pywemo) library, and has continud to work after Belkin's shutdown of the WeMo online services and app.

This README and project are not final, it will improve with time but I wanted to get this project out with the upcoming WeMo server shutdown.

### Requirements
For regular usage:
- Computer with Wi-Fi
- A relatively recent OS (Windows 11/macOS Sonoma/etc)
- WeMo device(s)

[For development](#development), you will need:
- Everything you'd need for regular usage
- Git
- Python 3.10 or newer
  - Pip & Tkinter must be supported
  - uv for a faster version of pip is a nice touch but not needed

### Getting PyWeMoGUI
You can download easy-to-run binaries of PyWeMoGUI on the [Releases](https://github.com/ThatStella7922/PyWeMoGUI/releases) page.

Binaries are available for Windows (tested) and macOS (mostly untested). If your OS doesn't have a binary available or you want to set up for running locally, see [the development instructions](#development)

## Using PyWeMoGUI
If you set up for running locally with [the development instructions](#development), see those instructions first.\
If you downloaded the binary from the [Releases](https://github.com/ThatStella7922/PyWeMoGUI/releases) then just run it like you would any other binary.

After a few seconds the main window should open and say "Autodiscovery in progress" in the list.

<img width=500 src=images/mainwindow.png>

After autodiscovery completes, any WeMos on your network will show up in the list. It'll show the name of the device, the type, the IP address, MAC address and serial number. You can click on a device in the list to select it.

You can right click inside of the list for quick actions, or you can use the buttons in the tabs below.

There are some tabs:
- Controls lets you:
  - Test a device by toggling it on/off
  - View a device's HomeKit details so you can add it to HomeKit
  - Change a device's name
  - Copy a device's IP address, MAC address or serial number
- Utilities lets you rescan devices and links to this page
- Setup WeMo contains everything required to setup a WeMo that has been reset, more on this later
- Reset WeMo lets you reset a WeMo's personalized info, Wi-Fi settings or even fully factory reset it.
- Debug is just for testing purposes and will have things inside that can appear nonsensical or even broken.

### Setting up a WeMo
To set up a WeMo, it has to be factory reset - or at the very least have had its Wi-Fi settings reset. You can reset it with PyWeMoGUI or via the WeMo itself, see the section below.

Once you are sure the WeMo is reset:
1. Plug it in/turn it on and wait for it to start up
2. Search for a WeMo Wi-Fi network nearby, something like "Wemo.Dim2G.295"
3. Connect to the WeMo's network, it should have no password
4. Open PyWeMoGUI or rescan devices if it's already open
5. You should see a single device in the table with the factory name of your device. For example a Dimmer will be named "Wemo Dimmer" in the list. Select it.
6. Navigate to the Setup WeMo tab, then enter the details of the Wi-Fi network you want the WeMo to connect to. If it has no password, check the 'No password/Open network' checkbox
7. If all goes well, your WeMo should reboot a few seconds later to apply its new settings.
8. After about a minute, it should be on your Wi-Fi network. You can then re-connect to your home Wi-Fi network and rescan for devices to see your Wemo!

### Resetting a WeMo
Select the WeMo you want to reset in the list, click the appropriate button for the reset you want to perform, then click Yes in the confirmation box. 

Resetting the WeMo via its hardware controls also works great.

The WeMo will restart after a few seconds to clear its settings. After about a minute, it should start broadcasting its Wi-Fi network.

## Development
### Manual setup
> [!NOTE]  
> If you do not want to develop PyWeMoGUI or manually set up for running locally, there are binaries on the [Releases](https://github.com/ThatStella7922/PyWeMoGUI/releases) page.

1. Clone the repo with git:\
`git clone https://github.com/thatstella7922/pywemogui`
2. Create a venv if you want to keep this self-contained
    - Run `python3 -m venv venv` to create it
    - Activate the venv:\
    Windows: `venv\Scripts\activate`\
    Linux/MacOS/*nix: `source venv/bin/activate`
3. Install the required packages:\
`pip install -r requirements.txt`

You can now run PyWeMoGUI by running `python3 main.py`.

Once you see the main window, you can refer back to the [usage instructions](#using-pywemogui) to use the app.

### Building
Since PyWeMoGUI is written in Python there is no build process. You can run it as-is.

The "build" process refers to creating a packaged binary with `pyinstaller`. To build a packaged binary, you can **first inspect** `build.py` to see how to use it, then run it. It supports command line arguments for skipping confirmation, logging to a file, or adjusting the log level, which can be useful for `pyinstaller`.

### "Roadmap"
- [ ] Refactor most device-related functions for more robust exception handling
- [x] QR code generation for HomeKit setup codes (WeMos can return an `X-HM://` URL for setup)
- [x] Renaming devices
- [ ] Device specific controls such as dimmer brightness
- [ ] Device specific configuration such as dimmer brightness *range*

### Contributing
I am not the best programmer by any stretch of the imagination so I really appreciate any help. Please fork & pull request if you have any code contributions, and if not, I also appreciate well-written issue reports. Both help and can make me aware of things that need improvement.

## Attribution and license
All rights are **not** reserved. https://github.com/pywemo/pywemo and https://github.com/iancmcc/ouimeaux are not my code and those belong to their respective authors. PyWeMoGUI is not endorsed by the pywemo or ouimeaux projects in any way. The PyWeMoGUI code is licensed under the GPLv3.