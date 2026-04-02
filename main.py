print("PyWeMoGUI by ThatStella7922 (https://thatstel.la)")

import argparse
import os
import traceback
import platform
parser = argparse.ArgumentParser(
    prog="PyWeMoGUI",
    description="A simple GUI that lets you manage your Belkin WeMo devices."
    )
parser.add_argument('--loglevel', '-l', help='Optionally define how verbose logs should be (default is INFO)', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
args = parser.parse_args()

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=f"{args.loglevel}", format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%I:%M:%S%p')
logger.info(f"This system is running {platform.system()} {platform.version()} ({platform.machine()}, {os.cpu_count()}x)")
logger.debug("Logger is up, importing the rest of the required modules...")

try:
    import tkinter as tk
    import tkinter.ttk as ttk # we don't use this right here but still worth trying to import it for error handling if it's not present
except ImportError as ie:
    logger.critical(f"Failed to import tkinter. Please check if you need a different Python distribution or maybe just need to install Tkinter. (Full: {repr(ie)})")
    exit(1)
from PyWeMoGUIApp import PyWeMoGUIApp


if __name__ == '__main__':
    logger.debug("Setting up Tk and initializing PyWeMoGUIApp...")
    try:
        root = tk.Tk()
        app = PyWeMoGUIApp(root)
        app.root.mainloop()
    except Exception as e:
        logger.error(f"Failed to initialize PyWeMoGUIApp: {repr(e)}\n                   {traceback.format_exc()}")
else:
    logger.critical("PyWeMoGUI is not designed to be used as a module. Please run it directly instead.")
    exit(1)