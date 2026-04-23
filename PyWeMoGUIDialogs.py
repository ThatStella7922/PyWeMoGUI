import logging
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import qrcode
from PIL import Image, ImageTk

class PyWeMoGUIHomeKitInfoDialog(tk.Toplevel):
    def __init__(self, parent, deviceName:str, setupURI: str, setupCode: str):
        self.logger = logging.getLogger(__name__)

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