import os
import logging
import shutil
import pywemo
import tkinter as tk
import tkinter.ttk as ttk
from queue import Queue, Empty
from tkinter import messagebox
from tkinter import simpledialog

from PyWeMoGUIDeviceManager import PyWeMoGUIDeviceManager

class PyWeMoGUIApp:
    def __init__(self, root: tk.Tk):
        self.logger = logging.getLogger(__name__)

        self.device_manager = PyWeMoGUIDeviceManager() # Instantiate a device manager early

        self.device_discovery_queue = Queue()
        '''
        This queue is used by the rescan_and_populate_device_list helper function to recieve data.
        '''

        # Start to create all GUI elements
        self.logger.info("Loading the GUI")
        self.root = root
        self.root.title("PyWeMoGUI")
        self.root.geometry("720x360")
        self.root.resizable(False, False)
        self.rescanDone = False

        ## Create device list
        self.devlist = ttk.Treeview(self.root)
        self.devlist['columns'] = ('type', 'ip', 'mac', 'serial')
        self.devlist.heading("#0", text="Name")
        self.devlist.heading("type", text="Type")
        self.devlist.heading("ip", text="IP Address")
        self.devlist.heading("mac", text="MAC Address")
        self.devlist.heading("serial", text="Serial Number")
        self.devlist.column("type", width=90)
        self.devlist.column("ip", width=100)
        self.devlist.column("mac", width=100)
        self.devlist.column("serial", width=100)
        self.devlist.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.logger.debug("Device list created")

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
        #self.tabDebug = ttk.Frame(self.tabs)
        #self.tabs.add(self.tabDebug, text="Debug") #### this should probably be tests instead of a tab with buttons but oh well lmao
        self.tabs.pack(expand=1, fill="both") #### pack to make visible
        self.logger.debug("Tabs created")

        ## Create buttons for 'Debug' tab
        #self.logger.debug("Debug tab buttons created")

        ## Create buttons for 'Controls' tab
        self.togglebutton = ttk.Button(self.tabControl, text="Test Device (Toggle)", command=self.toggle_device)
        self.renamebutton = ttk.Button(self.tabControl, text="Rename Device", command=self.rename_device_gui)
        self.gethomekitdetailsbutton = ttk.Button(self.tabControl, text="Get HomeKit details", command=self.get_hk_info_from_device)
        self.copyipaddressbutton = ttk.Button(self.tabControl, text="Copy IP Address", command=self.copy_device_ipaddress)
        self.copymacaddressbutton = ttk.Button(self.tabControl, text="Copy MAC Address", command=self.copy_device_macaddress)
        self.copyserialbutton = ttk.Button(self.tabControl, text="Copy Serial Number", command=self.copy_device_serial)
        self.togglebutton.grid(row=0, column=0, padx=5, pady=5)
        self.renamebutton.grid(row=0, column=1, padx=5, pady=5)
        self.gethomekitdetailsbutton.grid(row=1, column=0, padx=5, pady=5)
        self.copyipaddressbutton.grid(row=1, column=1, padx=5, pady=5)
        self.copymacaddressbutton.grid(row=1, column=2, padx=5, pady=5)
        self.copyserialbutton.grid(row=1, column=3, padx=5, pady=5)
        self.logger.debug("Controls tab buttons created")

        ## Create buttons for 'Utilities' tab
        self.aboutbutton = ttk.Button(self.tabUtils, text="About", command=self.show_about_dialog)
        self.helpbutton = ttk.Button(self.tabUtils, text="Help", command=self.show_help_dialog)
        self.rescandevicesbutton = ttk.Button(self.tabUtils, text="Rescan Devices", command=self.trigger_rescan_and_populate_device_list)
        self.aboutbutton.grid(row=0, column=0, padx=5, pady=5)
        self.helpbutton.grid(row=1, column=0, padx=5, pady=5)
        self.rescandevicesbutton.grid(row=0, column=1, padx=5, pady=5)
        self.logger.debug("Utilities tab buttons created")

        ## Create widgets for 'Setup WeMo' tab
        self.ssidinputlabel = ttk.Label(self.tabSetupWemo, text="WiFi SSID:")
        self.ssidinput = ttk.Entry(self.tabSetupWemo, width=25)
        self.passwordinputlabel = ttk.Label(self.tabSetupWemo, text="WiFi Password:")
        self.passwordinput = ttk.Entry(self.tabSetupWemo, width=25, show="●")
        self.nopasswordcheckboxvar = tk.IntVar()
        self.nopasswordcheckbox = ttk.Checkbutton(self.tabSetupWemo, text="No Password or Open network", command=self.handle_no_password_checkbox, variable=self.nopasswordcheckboxvar)
        self.setupbutton = ttk.Button(self.tabSetupWemo, text="Setup Device", command=self.setup_device)
        self.noteslabel = ttk.Label(self.tabSetupWemo, text="Note that sometimes Setting up a device can appear to fail but succeed anyway.")
        self.setupbutton.grid(row=2, column=3, padx=5, pady=0)
        self.ssidinputlabel.grid(row=1, column=0, padx=0, pady=5)
        self.ssidinput.grid(row=1, column=1, padx=0, pady=5)
        self.passwordinputlabel.grid(row=1, column=2, padx=0, pady=5)
        self.passwordinput.grid(row=1, column=3, padx=0, pady=5)
        self.nopasswordcheckbox.grid(row=2, column=1, padx=0, pady=0)
        self.noteslabel.grid(row=3, column=0, padx=0, pady=0, columnspan=4, rowspan=1)
        self.logger.debug("Setup WeMo tab widgets created")

        ## Create widgets for 'Reset WeMo' tab
        self.reset_personalized_info_button = ttk.Button(self.tabResetWemo, text="Reset (Clear Personalized Info)", command=lambda: self.reset_device("clear_personalized_info"))
        self.reset_wifi_button = ttk.Button(self.tabResetWemo, text="Reset (Change Wi-Fi)", command=lambda: self.reset_device("change_wifi"))    
        self.factory_reset_button = ttk.Button(self.tabResetWemo, text="Reset (Factory Reset)", command=lambda: self.reset_device("factory_reset"))
        self.reset_buttons_info_label = ttk.Label(self.tabResetWemo, text="Clear Personalized Info: Resets personalized settings only (name, icon, rules).\nChange Wi-Fi: Resets Wi-Fi settings only.\nFactory Reset: Resets all settings to factory defaults.")

        self.reset_personalized_info_button.grid(row=0, column=1, padx=5, pady=5)
        self.reset_wifi_button.grid(row=0, column=2, padx=5, pady=5)
        self.factory_reset_button.grid(row=0, column=3, padx=5, pady=5)
        self.reset_buttons_info_label.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        self.logger.debug("Reset WeMo tab widgets created")

        ## Create right click menu for the device list
        self.devlist_ctxmenu = tk.Menu(self.root, tearoff=0)
        self.devlist_ctxmenu.add_command(label="Device actions . . .", state='disabled')
        self.devlist_ctxmenu.add_command(label="Test Device (Toggle)", command=self.toggle_device)
        self.devlist_ctxmenu.add_command(label="Rename Device", command=self.rename_device_gui)
        self.devlist_ctxmenu.add_command(label="Copy IP Address", command=self.copy_device_ipaddress)
        self.devlist_ctxmenu.add_command(label="Copy MAC Address", command=self.copy_device_macaddress)
        self.devlist_ctxmenu.add_command(label="Copy serial number", command=self.copy_device_serial)
        self.devlist_ctxmenu.add_separator()
        self.devlist_ctxmenu.add_command(label="Rescan devices", command=self.trigger_rescan_and_populate_device_list)
        self.logger.debug("Device list right click menu created")
        
        ## Set up selection event and right click event
        self.devlist.bind("<<TreeviewSelect>>", self.on_tree_select) # bind selection event on device list to on_tree_select
        self.devlist.bind("<Button-3>", self.show_devlist_ctxmenu) # bind the right click on the device list to show context menu

        ## Start the periodic check of the device discovery queue so we don't miss device rescans providing new info
        self.check_device_discovery_queue()

        ## Finish and start a rescan for the user
        self.logger.info("GUI is ready, automatically starting device scan")
        self.trigger_rescan_and_populate_device_list()

    def check_device_discovery_queue(self):
        '''
        Checks the device discovery queue periodically to check for & apply new device data using populate_device_list.
        If nothing is found in the queue, nothing happens.
        
        This should always run in the background, ideally you should run it after the UI is done being set up but before the user does anything.
        '''
        try:
            #self.logger.debug("Checking the device discovery queue")
            message = self.device_discovery_queue.get(block=False)

            #this will run if there WAS something in the queue
            self.logger.debug("Populating device list with new data from queue")
            self.clear_device_list()
            self.device_manager.sort_list_by_name()
            self.populate_device_list(self.device_manager)
            self.rescanDone = True
        except Empty:
            pass
        self.root.after(500, self.check_device_discovery_queue)
    
    def toggle_device(self):
        '''
        Toggles the selected device. For most devices this will result in turning it off/on.
        '''
        try:
            device = self.get_selected_device()
            device.toggle()
            self.logger.debug(f"Toggled device {device.name}")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        except Exception as e:
            self.logger.error(f"Failed to toggle device '{device.name}' because of the following error: {repr(e)}")
            messagebox.showerror("Error", f"Could not toggle '{device.name}' because of the following error:\n{repr(e)}")

    def rename_device_gui(self):
        '''
        Shows a dialog with a text box for the user to change a WeMo's name
        '''
        try:
            device = self.get_selected_device()
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        new_name = self.show_askstringdialog("PyWeMoGUI - Rename", f"Enter a new name for the device '{device.name}':", preset_string=device.name)
        if new_name:
            try:
                self.rename_device(new_name, device)
                self.show_infodialog("PyWeMoGUI - Rename", f"Successfully renamed the device to '{new_name}'.\nA device rescan will now occur to reflect the new name!")
                self.trigger_rescan_and_populate_device_list()
            except Exception as e:
                self.logger.error(f"Failed to rename device '{device.name}' because of the following error: {repr(e)}")
                messagebox.showerror("Error", f"Could not rename '{device.name}' because of the following error:\n{repr(e)}")

    def get_hk_info_from_device(self):
        '''
        Gets the HomeKit setup **state** and setup **code** from the selected device, then displays it in an info dialog.
        '''
        try:
            device = self.get_selected_device()
            device_name = device.name
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        try:
            setupState = self.get_hksetupstate_from_device(device)["HKSetupDone"]
            setupCode = self.get_hksetupcode_from_device(device)["HKSetupCode"]
        except Exception as e:
            self.logger.error(f"Failed to get HomeKit details for device '{device_name}' because of the following error: {repr(e)}")
            messagebox.showerror("PyWeMoGUI - Error", f"Failed to acquire the HomeKit details from the WeMo.\nAdditional info: {repr(e)}")
        if setupState == "1":
            setupStateFriendly = "set up"
        else:
            setupStateFriendly = "not set up"
        self.show_infodialog("PyWeMoGUI - HomeKit details", f"{device_name}'s setup code is {setupCode}.\nThis WeMo is currently {setupStateFriendly} with HomeKit")
    
    def setup_device(self):
        '''
        Sets up a device with the specified Wi-Fi credentials
        '''
        self.logger.debug("Preparing to set up the selected device")
        try:
            device=self.get_selected_device()
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
            self.logger.info(f"Starting setup for the '{device.name}' with SSID '{ssid}'. PyWeMoGUI will appear to be unresponsive while set up is in progress!\nThis will be fixed in a future version.")
            self.show_infodialog("PyWeMoGUI - Setup", f"Starting setup for the '{device.name}'. PyWeMoGUI will appear to be unresponsive while set up is in progress!")
            setupResult = device.setup(ssid=ssid, password=password)
        except pywemo.exceptions.APNotFound as apnfe:
            self.logger.error(f"Setup didn't succeed for '{device.name}' because the WeMo couldn't find the '{ssid}' Wi-Fi network: {repr(apnfe)}")
            messagebox.showerror("Setup Error - PyWeMoGUI", f"Setup did not succeed for '{device.name}' because the WeMo couldn't find the '{ssid}' Wi-Fi network.\nPlease check that your WeMo is in range of the Wi-Fi network and that you entered the SSID correctly.")
        except pywemo.exceptions.SetupException as se:
            self.logger.error(f"Setup didn't succeed for '{device.name}' because of the following setup error: {repr(se)}")
            messagebox.showerror("Setup Error - PyWeMoGUI", f"Setup did not succeed for '{device.name}' because of the following error:\n{se}\n\nIn some rare cases, the device might have actually been set up in spite of this error. You can re-connect to your home Wi-Fi and do a rescan to see if your new device is detected!")
        except pywemo.exceptions.ShortPassword as spe:
            self.logger.error(f"Setup didn't succeed for '{device.name}' because the password provided is too short: {repr(spe)}")
            messagebox.showerror("Setup Error - PyWeMoGUI", f"Setup did not succeed for '{device.name}' because the password provided is too short. WeMo Wi-Fi passwords must be at least 8 characters long.\n\nMaybe you meant to check the 'No Password/Open Network' box?")
        except Exception as e:
            self.logger.error(f"Failed to start setup for device '{device.name}' because of the following error: {repr(e)}")
            messagebox.showerror("Error - PyWeMoGUI", f"Failed to start setup for device '{device.name}' because of the following error: {repr(e)}")
        self.logger.info(f"Setup appears to have succeeded for '{device.name}'. Network status was {setupResult[0]} and close status was {setupResult[1]}")
        self.show_infodialog("PyWeMoGUI -  Setup", f"Setup appears to have succeeded for '{device.name}'. Please reconnect to your home Wi-Fi and do a rescan to see if your new device is detected!")
        
    def reset_device(self, reset_type):
        '''
        Resets the selected device according to the specified reset type.

        :param reset_type: Must be one of three strings:
        - "clear_personalized_info" - Resets personalized settings only (name, icon, rules).
        - "change_wifi" - Resets Wi-Fi settings only.
        - "factory_reset" - Resets all settings to factory defaults.
        '''
        try:
            selected=self.get_selected_device()
            device_name=selected.name
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        if self.confirm_action("Confirm", f"Are you sure you want to perform a reset ({reset_type}) on the '{device_name}'? This action cannot be undone."):
            match reset_type:
                case "clear_personalized_info":
                    try:
                        selected.reset(data=True, wifi=False)
                    except Exception as e:
                        self.logger.error(f"Failed to reset (clear personalized info) for device '{device_name}' because of the following error: {repr(e)}")
                        messagebox.showerror("Error", f"Failed to reset (clear personalized info) for device {device_name}: {repr(e)}")
                case "change_wifi":
                    try:
                        selected.reset(data=False, wifi=True)
                    except Exception as e:
                        self.logger.error(f"Failed to reset (change WiFi) for device '{device_name}' because of the following error: {repr(e)}")
                        messagebox.showerror("Error", f"Failed to reset (change WiFi) for device {device_name}: {repr(e)}")
                case "factory_reset":
                    try:
                        selected.reset(data=True, wifi=True)
                    except Exception as e:
                        self.logger.error(f"Failed to reset (factory reset) for device '{device_name}' because of the following error: {repr(e)}")
                        messagebox.showerror("Error", f"Failed to reset (factory reset) device {device_name}: {repr(e)}")        
    
    def handle_no_password_checkbox(self):
        if self.nopasswordcheckboxvar.get() == 1:
            self.passwordinput.delete(0, tk.END)
            self.passwordinput.config(state='disabled')
        else:
            self.passwordinput.config(state='normal')

    def show_devlist_ctxmenu(self, event):
        try:
            self.devlist_ctxmenu.tk_popup(event.x_root, event.y_root)
        finally:
            self.devlist_ctxmenu.grab_release()

    def copy_device_ipaddress(self):
        try:
            device = self.get_selected_device()
            ip_address = device.host
            self.root.clipboard_clear()
            self.root.clipboard_append(ip_address)
            self.logger.info(f"Copied {device.name}'s IP address '{ip_address}' to clipboard")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy IP address because of the following error:\n{repr(e)}")

    def copy_device_macaddress(self):
        try:
            device = self.get_selected_device()
            mac_address = device.basicevent.GetMacAddr()['MacAddr']
            if not mac_address:
                raise Exception(f"{device.name} did not provide a MAC address or it is unavailable")
            self.root.clipboard_clear()
            self.root.clipboard_append(mac_address)
            self.logger.info(f"Copied {device.name}'s MAC address '{mac_address}' to clipboard")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy MAC address because of the following error:\n{repr(e)}")

    def copy_device_serial(self):
        '''
        Copies the selected device's serial number to the clipboard.
        '''
        try:
            device = self.get_selected_device()
            serial_number = device.basicevent.GetMacAddr()['SerialNo']
            if not serial_number:
                raise Exception(f"{device.name} did not provide a serial number or it is unavailable")
            self.root.clipboard_clear()
            self.root.clipboard_append(serial_number)
            self.logger.info(f"Copied {device.name}'s serial number '{serial_number}' to clipboard")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy serial number because of the following error:\n{repr(e)}")

    def on_tree_select(self, event):
        if self.rescanDone:
            try:
                pass
            ### Do nothing here because we don't need to do anything, not entirely sure why I had this block
            ### here just printing the device's name when a new one was selected.
            except ValueError as ve:
                messagebox.showerror("Error", str(ve))
                return
            #self.logger.debug(f"Selected device: {device_name}")
        else:
            self.logger.debug("Ignored selection in device list because rescan isn't done")
        
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
        self.logger.debug(f"Index of the selected device is {device_index}")
        device = self.device_manager.get_device_by_array_index(device_index) #maybe add throws to this function
        self.logger.debug(f"Device object is {device}")
        return device

    def trigger_rescan_and_populate_device_list(self):
        '''
        Rescan devices and populate the UI with the new data when called. This function sets the global variable to inform that a rescan is in progress.
        
        **This is the preferred method** to call when you need to scan for new devices. It clears out the UI, populates the placeholder, and sets up the device list with new devices.

        It will:
        1. Clear the device list
        2. Populate the device list with a placeholder
        3. Ask the device manager to discover devices and put the results (if any) in the `device_discovery_queue`

        To act upon the results, the `device_discovery_queue` is checked by `check_device_discovery_queue` periodically.
        '''
        self.logger.debug("Performing a full device rescan and population of the device list")
        self.rescanDone = False
        self.clear_device_list()
        self.populate_auto_discovery_placeholder_in_list()
        self.device_manager.discover_devices(self.device_discovery_queue)        

    def populate_device_list(self, device_manager):
        '''
        Populates each device into the device list with device name, model, IP, MAC address and serial

        # TODO
        This function **needs** to recieve data from its caller instead of reading the device manager's devices list directly!
        
        Data put into the device discovery queue is not used, and the periodic checker just calls this when new data is found
        '''
        for device in device_manager.current_devices:
            try:
                devInfo = device.basicevent.GetMacAddr()
                                             # Device Name        # Device Type       # IP Address        # MAC Address         # Serial Number
            except Exception as e:
                self.logger.warning(f"Device {device.name} lacks the GetMacAddr() basicevent so its MAC address and serial number will not be available")
                devInfo = {'MacAddr': 'Unknown', 'SerialNo': 'Unknown'}
            self.logger.debug(f"Listing device: {device.name} ({device.model_name}), {device.host}, {devInfo['MacAddr']}, {devInfo['SerialNo']}")
            self.devlist.insert('', 'end', text=device.name, values=(device.model_name, device.host, devInfo['MacAddr'], devInfo['SerialNo']))

    def populate_auto_discovery_placeholder_in_list(self):
        '''
        Insert a placeholder letting the user know that device discovery is happening and that they should wait.
        
        Appends to anything already inside the list, so consider **clearing the device list before using**
        '''
        self.devlist.insert('', 'end', text="Autodiscovery in progress", values=("please wait", "", "", ""))

    def clear_device_list(self):
        '''Clear the device list, removing all items (including placeholders)'''
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
        self.logger.info(f"Checking that {progtocheck} is accessible to us")
        executable_path = shutil.which(progtocheck)
        if executable_path:
            self.logger.debug(f"The path for the executable is: {executable_path}")
            self.show_infodialog(f"PyWeMoGUI - Checking {progtocheck}", f"The program {progtocheck} was found in the PATH.\n\nIt was found at: {executable_path}")
        else:
            self.logger.error(f"{progtocheck} wasn't found in PATH.\n            PATH searched:\n{os.environ.get("PATH")}\n            Maybe the directory containing {progtocheck} is missing from your PATH?")
            self.show_infodialog(f"PyWeMoGUI - Checking {progtocheck}", f"PyWeMoGUI was not able to find {progtocheck} in the PATH.\nAdditional information is available in the console.")

    def get_hksetupstate_from_device(self, device: pywemo.ouimeaux_device.Device):
        #TODO parse the dict in here instead requiring caller to parse
        '''
        Docstring for get_hksetupstate_from_device
        
        :param self: Description
        :param device: Device to get the HomeKit setup state from
        :type device: pywemo.ouimeaux_device.Device
        '''
        self.logger.debug("Getting HKSetupState from device")
        try:
            action = device.basicevent.getHKSetupState
            self.logger.debug(action())
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
        self.logger.debug("Getting HKSetupCode from device")
        try:
            action = device.basicevent.GetHKSetupInfo
            self.logger.debug(action())
            return (action())
        except Exception as e:
            raise Exception(e)
        
    def rename_device(self, name: str, device: pywemo.ouimeaux_device.Device):
        '''
        Change a WeMo's name to the specified value
        
        :param name: New name for the WeMo
        :param device: Device to get the HomeKit setup state from
        :type device: pywemo.ouimeaux_device.Device
        '''
        self.logger.info("Renaming device")
        try:
            action = device.basicevent.ChangeFriendlyName(FriendlyName=name)
            self.logger.debug(action)
            return (action)
        except Exception as e:
            raise Exception(e)
        
    def show_infodialog(self, title, message):
        '''
        Show an info dialog with the specified title and message.
        
        :param title: Title for the info dialog
        :param message: Description for the info dialog
        '''
        messagebox.showinfo(title=title, message=message)

    def show_askstringdialog(self, title: str, prompt: str, preset_string: str=""):
        '''
        Show a dialog with a textfield that can accept a string.
        If the user cancels None is returned, otherwise the string is returned.
        
        :param title: Title for the dialog
        :type title: str
        :param prompt: Prompt "please enter ..." for the dialog
        :type prompt: str
        :param preset_string: A preset value to show in the textfield (Optional)
        :type preset_string: str
        '''
        return simpledialog.askstring(title= title, prompt = prompt, initialvalue = preset_string)
    
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