### Version 1.0 i guess

import pywemo
import tkinter as tk
import tkinter.ttk as ttk
import threading
from tkinter import messagebox
from tkinter import simpledialog
import os
import traceback
import shutil

class Logger:
    '''
    Docstring for Logger
    
    :var will: it logs to console with log, debug, info, warn and error levels
    '''
    def __init__(self, prefix="PyWeMoGUI"):
        self.enableDebugs = False
        self.prefix = prefix

    def log(self, message):
        print(f"[{self.prefix}] {message}")

    def error(self, message):
        print(f"[{self.prefix}] ERROR: {message}")

    def warn(self, message):
        print(f"[{self.prefix}] WARNING: {message}")

    def info(self, message):
        print(f"[{self.prefix}] INFO: {message}")

    def debug(self, message):
        if self.enableDebugs:
            print(f"[{self.prefix}] DEBUG: {message}")

    def setDebugs(self, val: bool):
        if val:
            self.enableDebugs = True
            self.debug("Debug logging enabled")
        else:
            self.debug("Debug logging was disabled")
            self.enableDebugs = False
class PyWeMoGUIApp:
    def __init__(self, root, logger: Logger):
        self.logger = logger
        logger.setDebugs(True)
        self.root = root
        logger.debug("Starting GUI")
        self.root.title("PyWeMoGUI")
        self.root.geometry("640x360")
        self.root.resizable(False, False)
        self.rescanDone = False

        # Create and place widgets
        ## Create device list
        self.devlist = ttk.Treeview(self.root)
        self.devlist['columns'] = ('type', 'ip')
        self.devlist.heading("#0", text="Name")
        self.devlist.heading("type", text="Type")
        self.devlist.heading("ip", text="IP Address")
        self.devlist.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ## Add tabs to root
        self.tabs = ttk.Notebook(root) ### instantiate
        self.tabControl = ttk.Frame(self.tabs) #### instantiate child tabControl
        self.tabs.add(self.tabControl, text='Controls') #### name it and add to tabs
        self.tabUtils = ttk.Frame(self.tabs) #### instantiate child tabSettings
        self.tabs.add(self.tabUtils, text='Utilities') #### name it and add to tabs
        self.tabSetupWemo = ttk.Frame(self.tabs) #### instantiate child tabSetupWemo
        self.tabs.add(self.tabSetupWemo, text='Setup WeMo') #### name it and add to tabs
        self.tabResetWemo = ttk.Frame(self.tabs) #### instantiate child tabResetWemo
        self.tabs.add(self.tabResetWemo, text='Reset WeMo') #### name it and add to tabs
        self.tabs.pack(expand=1, fill="both") #### pack to make visible

        ## Create buttons for 'Controls' tab
        self.togglebutton = ttk.Button(self.tabControl, text="Test Device (Toggle)", command=self.toggle_device)
        self.togglebutton.grid(row=0, column=0, padx=5, pady=5)

        ## Create buttons for 'Utilities' tab
        self.aboutbutton = ttk.Button(self.tabUtils, text="About", command=self.show_about_dialog)
        self.helpbutton = ttk.Button(self.tabUtils, text="Help", command=self.show_help_dialog)
        self.checkopensslbutton = ttk.Button(self.tabUtils, text="Check for OpenSSL", command=lambda: self.check_program_accessible("openssl"))
        self.acquirehomekitdetailsbutton = ttk.Button(self.tabUtils, text="Acquire HomeKit details from WeMo", command=self.get_hk_info_from_device)
        self.rescandevicesbutton = ttk.Button(self.tabUtils, text="Rescan Devices", command=self.trigger_rescan)
        self.aboutbutton.grid(row=0, column=0, padx=5, pady=5)
        self.helpbutton.grid(row=1, column=0, padx=5, pady=5)
        self.checkopensslbutton.grid(row=0, column=2, padx=5, pady=5)
        self.acquirehomekitdetailsbutton.grid(row=0, column=3, columnspan=2, padx=5, pady=5)
        self.rescandevicesbutton.grid(row=0, column=1, padx=5, pady=5)

        ## Create widgets for 'Setup WeMo' tab
        self.ssidinputlabel = ttk.Label(self.tabSetupWemo, text="WiFi SSID:")
        self.ssidinput = ttk.Entry(self.tabSetupWemo, width=30)
        self.passwordinputlabel = ttk.Label(self.tabSetupWemo, text="WiFi Password:")
        self.passwordinput = ttk.Entry(self.tabSetupWemo, width=30, show="*")
        self.nopasswordcheckboxvar = tk.IntVar()
        self.nopasswordcheckbox = ttk.Checkbutton(self.tabSetupWemo, text="No Password or Open network", command=self.handle_no_password_checkbox, variable=self.nopasswordcheckboxvar)
        self.setupbutton = ttk.Button(self.tabSetupWemo, text="Setup Device", command=self.setup_device)
        self.noteslabel = ttk.Label(self.tabSetupWemo, text="Note that in order to set up WeMos with a Wi-Fi password,\nOpenSSL needs to be installed and usable as `openssl` from the commandline.")
        self.setupbutton.grid(row=2, column=3, padx=5, pady=0)
        self.ssidinputlabel.grid(row=1, column=0, padx=0, pady=5)
        self.ssidinput.grid(row=1, column=1, padx=0, pady=5)
        self.passwordinputlabel.grid(row=1, column=2, padx=0, pady=5)
        self.passwordinput.grid(row=1, column=3, padx=0, pady=5)
        self.nopasswordcheckbox.grid(row=2, column=1, padx=0, pady=0)
        self.noteslabel.grid(row=3, column=0, padx=0, pady=0, columnspan=4, rowspan=1)

        ## Create widgets for 'Reset WeMo' tab
        self.reset_personalized_info_button = ttk.Button(self.tabResetWemo, text="Reset (Clear Personalized Info)", command=lambda: self.reset_device("clear_personalized_info"))
        self.reset_wifi_button = ttk.Button(self.tabResetWemo, text="Reset (Change Wi-Fi)", command=lambda: self.reset_device("change_wifi"))    
        self.factory_reset_button = ttk.Button(self.tabResetWemo, text="Reset (Factory Reset)", command=lambda: self.reset_device("factory_reset"))
        self.reset_buttons_info_label = ttk.Label(self.tabResetWemo, text="Clear Personalized Info: Resets personalized settings only (name, icon, rules).\nChange Wi-Fi: Resets Wi-Fi settings only.\nFactory Reset: Resets all settings to factory defaults.")

        self.reset_personalized_info_button.grid(row=0, column=1, padx=5, pady=5)
        self.reset_wifi_button.grid(row=0, column=2, padx=5, pady=5)
        self.factory_reset_button.grid(row=0, column=3, padx=5, pady=5)
        self.reset_buttons_info_label.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        logger.log("GUI is ready")
        self.devlist.bind("<<TreeviewSelect>>", self.on_tree_select)
        logger.log("Automatically starting device scan")
        self.trigger_rescan()
    
    def toggle_device(self):
        '''
        Toggles the selected device. For most devices this will result in turning it off/on.
        '''
        try:
            device = self.get_selected_device()
            device.toggle()
            logger.debug(f"Toggled device {device.name}")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        except Exception as e:
            messagebox.showerror("Error", f"Could not toggle '{device.name}' because of the following error:\n{repr(e)}")

    def get_hk_info_from_device(self):
        '''
        Gets the HomeKit setup **state** and setup **code** from the selected device, then displays it in an info dialog.
        '''
        try:
            selected=self.get_selected_device_DEPRECATED()
            device_name = self.devlist.item(selected, 'text')
            device = self.device_manager.get_device_by_name(device_name)
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        try:
            setupState = self.get_hksetupstate_from_device(device)["HKSetupDone"]
            setupCode = self.get_hksetupcode_from_device(device)["HKSetupCode"]
        except Exception as e:
            messagebox.showerror("PyWeMoGUI - Error", f"Failed to acquire the HomeKit details from the WeMo.\nAdditional info: {repr(e)}")
        if setupState == "1":
            setupStateFriendly = "set up"
        else:
            setupStateFriendly = "not set up"
        self.show_infodialog("PyWeMoGUI - HomeKit details", f"{device_name}'s setup code is {setupCode}.\nThis WeMo is currently {setupStateFriendly} with HomeKit")

    def trigger_rescan(self):
        '''
        Prepares for, then runs a device discovery (re)scan. This function **will** set the helper variable to inform that a rescan is in progress, unlike setup_device_list.
        '''
        logger.debug("Doing full device rescan")
        self.rescanDone = False
        self.clear_device_list()
        self.populate_placeholder_in_list()
        self.setup_device_list()
    
    def setup_device(self):
        '''
        Sets up a device with the specified Wi-Fi credentials
        '''
        try:
            selected=self.get_selected_device_DEPRECATED()
            device_name=self.devlist.item(selected, 'text')
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        try:
            if not self.ssidinput.get():
                messagebox.showerror("Error", "Wi-Fi credentials cannot be empty.")
                return
            if not self.passwordinput.get() and self.nopasswordcheckboxvar.get() == 0:
                messagebox.showerror("Error", "Wi-Fi password cannot be empty unless 'Open/No Password' is checked.")
                return
            
            # Prepare WiFi credentials
            ssid = self.ssidinput.get()
            password = self.passwordinput.get()
            if self.passwordinput.get() == "" and self.nopasswordcheckboxvar.get() == 1:
                password = None
            self.device_manager.get_device_by_name(device_name).setup(ssid=ssid, password=password)
        except pywemo.exceptions.SetupException as se:
            messagebox.showerror("Setup Error", f"Setup did not succeed for '{device_name}' because of the following error:\n{se}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start setup for device '{device_name}' because of the following error: {repr(e)}")
        
    def reset_device(self, reset_type):
        '''
        Resets the selected device according to the specified reset type.

        :param reset_type: Must be one of three strings:
        - "clear_personalized_info" - Resets personalized settings only (name, icon, rules).
        - "change_wifi" - Resets Wi-Fi settings only.
        - "factory_reset" - Resets all settings to factory defaults.
        '''
        try:
            selected=self.get_selected_device_DEPRECATED()
            device_name=self.devlist.item(selected, 'text')
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        if self.confirm_action("Confirm", f"Are you sure you want to perform a reset ({reset_type}) on the '{device_name}'? This action cannot be undone."):
            match reset_type:
                case "clear_personalized_info":
                    try:
                        self.device_manager.get_device_by_name(device_name).reset(data=True, wifi=False)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to reset (clear personalized info) for device {device_name}: {repr(e)}")
                case "change_wifi":
                    try:
                        self.device_manager.get_device_by_name(device_name).reset(data=False, wifi=True)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to reset (change WiFi) for device {device_name}: {repr(e)}")
                case "factory_reset":
                    try:
                        self.device_manager.get_device_by_name(device_name).reset(data=True, wifi=True)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to reset (factory reset) device {device_name}: {repr(e)}")        
    
    def handle_no_password_checkbox(self):
        if self.nopasswordcheckboxvar.get() == 1:
            self.passwordinput.delete(0, tk.END)
            self.passwordinput.config(state='disabled')
        else:
            self.passwordinput.config(state='normal')

    def on_tree_select(self, event):
        if self.rescanDone:
            try:
                selected=self.get_selected_device_DEPRECATED()
                device_name=self.devlist.item(selected, 'text')
            except ValueError as ve:
                messagebox.showerror("Error", str(ve))
                return
            logger.info(f"Selected device: {device_name}")
        else:
            logger.info("Ignored selection in device list because rescan isn't done")

    def get_selected_device_DEPRECATED(self):
        '''
        imagine get_selected_device_promax but worse and needs all the error handling in the caller
        '''
        selected=self.devlist.focus()
        if selected:
            return selected
        else: 
            raise ValueError("No device selected")
        
    def get_selected_device(self) -> pywemo.ouimeaux_device.Device:
        '''
        Return a pywemo device object for whatever device is selected in the list.
        Make sure the caller can catch or passthrough exceptions.

        ## Throws
        `ValueError` if there is no selected device

        :returns: The selected device as a pywemo device object
        :rtype: pywemo.ouimeaux_device.Device
        '''
        lineitem = self.devlist.selection()
        if not lineitem:
            raise ValueError("There is no device selected")
        device_index = self.devlist.index(lineitem[0])
        logger.debug(f"Index of the selected device is {device_index}")
        device = self.device_manager.get_device_by_array_index(device_index) #maybe add throws to this function
        logger.debug(f"Device object is {device}")
        return device

    def setup_device_list(self):
        '''
        Utility function that gets the device list ready to go when called. It will:
        1. Create a device manager to put devices into
        2. Create a thread
        3. In the thread, run device discovery
        4. In the thread, clear the device list
        5. In the thread, populate the device list with what was discovered
        6. In the thread, set a helper variable to inform other functions that a rescan is not in progress

        This function will **not** set the helper variable to inform that a rescan is in progress.
        '''
        logger.debug("Starting device discovery thread")
        self.device_manager = devices()
        def threaded_discovery():
            self.device_manager.discover_devices()
            self.clear_device_list()
            self.populate_device_list(self.device_manager)
            self.rescanDone = True
        scanThread = threading.Thread(target=threaded_discovery)
        scanThread.start()

    def populate_device_list(self, device_manager):
        for device in device_manager.devices:
            logger.debug(f"Listing device: {device.name} ({device.model_name}) at {device.host}")
            self.devlist.insert('', 'end', text=device.name, values=(device.model_name, device.host))

    def populate_placeholder_in_list(self):
        self.devlist.insert('', 'end', text="Autodiscovery in progress", values=("please wait", ""))

    def clear_device_list(self):
        for item in self.devlist.get_children():
            self.devlist.delete(item)

    def check_program_accessible(self, progtocheck: str):
        '''
        Checks if a specified program is available to PyWeMoGUI on the PATH.
        Needs refactoring.
        
        :param progtocheck: Binary name to search for on the PATH
        :type progtocheck: str
        '''
        #TODO maybe make this a generic that doesn't show dialogs but instead returns a path or throws exception, both to be consumed from a check_openssl_accessible function?
        logger.info(f"Checking that {progtocheck} is accessible to us")
        executable_path = shutil.which(progtocheck)
        if executable_path:
            logger.debug(f"The path for the executable is: {executable_path}")
            self.show_infodialog(f"PyWeMoGUI - Checking {progtocheck}", f"The program {progtocheck} was found in the PATH.\n\nIt was found at: {executable_path}")
        else:
            logger.error(f"{progtocheck} wasn't found in PATH.\n            PATH searched:\n{os.environ.get("PATH")}\n            Maybe the directory containing {progtocheck} is missing from your PATH?")
            self.show_infodialog(f"PyWeMoGUI - Checking {progtocheck}", f"PyWeMoGUI was not able to find {progtocheck} in the PATH.\nAdditional information is available in the console.")

    def get_hksetupstate_from_device(self, device: pywemo.ouimeaux_device.Device):
        #TODO parse the dict in here instead requiring caller to parse
        '''
        Docstring for get_hksetupstate_from_device
        
        :param self: Description
        :param device: Device to get the HomeKit setup state from
        :type device: pywemo.ouimeaux_device.Device
        '''
        logger.info("Getting HKSetupState from device")
        try:
            action = device.basicevent.getHKSetupState
            logger.debug(action())
            return (action())
        except Exception as e:
            raise Exception(e)
    
    def get_hksetupcode_from_device(self, device: pywemo.ouimeaux_device.Device):
        #TODO parse the dict in here instead requiring caller to parse
        '''
        Gets the HomeKit setup code from a specified device
        
        :param device: Device to get the HomeKit setup code from
        :type device: pywemo.ouimeaux_device.Device
        '''
        logger.info("Getting HKSetupCode from device")
        try:
            action = device.basicevent.GetHKSetupInfo
            logger.debug(action())
            return (action())
        except Exception as e:
            raise Exception(e)
        
    def show_infodialog(self, title, message):
        '''
        Show an info dialog with the specified title and message.
        
        :param title: Title for the info dialog
        :param message: Description for the info dialog
        '''
        messagebox.showinfo(title=title, message=message)
    
    def confirm_action(self, title, message):
        '''
        Show an "are you sure?" dialog with the specified title and message.
        
        :param title: Title for the dialog
        :param message: Description for the dialog

        :returns bool: True if accepted, False if canceled.
        '''
        return messagebox.askokcancel(title, message)
    
    def show_about_dialog(self):
        self.show_infodialog("About PyWeMoGUI", "PyWeMoGUI\nA simple GUI for managing WeMo devices. Built on the PyWeMo library, not supported or endorsed by PyWeMo contributors\n\nhttps://github.com/thatstella7922/pywemogui\nThatStella7922 2026")

    def show_help_dialog(self):
        self.show_infodialog("PyWeMoGUI help", "You can visit the README for PyWeMoGUI at\nhttps://github.com/thatstella7922/pywemogui\nfor help")
        
class devices:
    def __init__(self):
        self.devices = []

    def discover_devices(self):
        self.devices = pywemo.discover_devices()

    def list_devices(self):
        return [device.name for device in self.devices]

    def get_device_by_name(self, name):
        '''
        Returns the device with the specified name
        
        :param index: The name of the device in the table to return
        '''
        for device in self.devices:
            if device.name == name:
                return device
        return None
    
    def get_device_by_ip(self, ip):
        '''
        Returns the device with the specified IP
        
        :param index: The IP of the device in the table to return
        '''
        for device in self.devices:
            if device.host == ip:
                return device
        return None
    
    def get_device_by_array_index(self, index: int): # Probably more performant than by name or ip
        '''
        Returns the device with the specified index
        
        :param index: The index of the device in the table to return
        '''
        if 0 <= index < len(self.devices):
            return self.devices[index]
        return None

if __name__ == '__main__':
    logger = Logger()
    logger.log("Initializing...")
    try:
        root = tk.Tk()
        app = PyWeMoGUIApp(root, logger)
        root.mainloop()
    except Exception as e:
        logger.error(f"Failure while initializing PyWeMoGUIApp: {repr(e)}\n                   {traceback.format_exc()}")