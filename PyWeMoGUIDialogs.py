import logging
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import qrcode
from PIL import Image, ImageTk

class PyWeMoGUIHomeKitInfoDialog(tk.Toplevel):
    '''This dialog provides nice-looking HomeKit information to the user about their WeMo.
    
    Provide the device name, setup URI and setup code and this dialog will automatically format the info to look nice.
    
    Setup URI will be turned into a QR code for scanning and the setup code will be displayed with a "copy to clipboard" button.'''
    def __init__(self, parent, deviceName:str, setupURI: str, setupCode: str):
        self.logger = logging.getLogger(f"{__name__} HomeKitInfoDialog")

        # window setup
        self.logger.debug("Initializing homekit info dialog now")
        super().__init__(parent)
        self.title(f"HomeKit info for {deviceName} - PyWeMoGUI")
        self.geometry("300x400")
        self.resizable(False, False)

        # make the damn qr code
        self.logger.debug("Generating QR code")
        qr_code_image = qrcode.make(setupURI)
        qr_code_image = qr_code_image.resize((300, 300), Image.Resampling.NEAREST)
        tkimage = ImageTk.PhotoImage(qr_code_image)

        panel = tk.Label(self, image = tkimage)
        panel.image = tkimage
        subtitletext = ttk.Label(self, wraplength=300 ,text=f"You can scan this QR code with your iOS device to add the '{deviceName}' WeMo to HomeKit, or use the setup code below.")
        code_label = ttk.Label(self, text=f"Setup code: {setupCode}")
        copy_clipboard_button = ttk.Button(self, text="Copy to clipboard", command=lambda: self.copy_setup_code_to_clipboard(setupCode))

        # put everything on the window
        panel.grid(row=0, column=0, columnspan=2, padx=0 ,pady=10)
        subtitletext.grid(row=1, column=0, columnspan=3, padx=10, pady=0)
        code_label.grid(row=2, column=0, padx=10, pady=10)
        copy_clipboard_button.grid(row=2, column=1, padx=0, pady=0)
        
    def copy_setup_code_to_clipboard(self, setupCode):
        try:
            self.clipboard_clear()
            self.clipboard_append(setupCode)
            self.logger.info("HomeKit setup code copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy IP address because of the following error:\n{repr(e)}")

class PyWeMoGUIAboutDialog(tk.Toplevel):
    '''probably in the future going to be a nice about dialog that's fancy with an image for a potential pywemogui logo'''
    def __init__(self, parent):
        self.logger = logging.getLogger(f"{__name__} AboutDialog")

        # window setup
        super().__init__(parent)
        self.title("About PyWeMoGUI")
        self.geometry("400x200")
        self.resizable(False, False)

        about_text = "PyWeMoGUI\nA simple GUI that lets you manage your Belkin WeMo devices.\n\nPyWeMoGUI is built on the pyWeMo library and is not supported or endorsed by pyWeMo contributors.\n\nhttps://github.com/ThatStella7922/PyWeMoGUI\nhttps://thatstel.la\nThatStella7922 2026"
        about_label = ttk.Label(self, wraplength=380 ,text=about_text)
        about_label.pack(padx=10, pady=10)

class PyWeMoGUIHelpDialog(tk.TopLevel):
    '''Full help dialog with tabs covering different help topics'''
    def __init__(self, parent):
        self.logger = logging.getLogger(f"{__name__} HelpDialog")

        #set the window up
        super().__init__(parent)
        self.title("PyWeMoGUI Help")

        pass
        #TODO: Finish this help dialog, figure out where it's going to pull help data from, figure out how to display it