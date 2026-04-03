print("PyWeMoGUI by ThatStella7922 (https://thatstel.la)")

import argparse
import os
import traceback
import platform
import logging
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(
    prog="PyWeMoGUI",
    description="A simple GUI that lets you manage your Belkin WeMo devices.",
    color=True
    )
parser.add_argument('--loglevel', '-l', help='Optionally define how verbose logs should be (default is INFO)', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
args = parser.parse_args()

# Logger configuration and basic system info retrieval
#TODO Optional argument for logging to file
logging.basicConfig(level=f"{args.loglevel}", format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%I:%M:%S%p')
logger.info(f"Logger started, loglevel is set to {args.loglevel}")
logger.info(f"Running on {platform.system()} {platform.version()} ({platform.machine()}, {os.cpu_count()}x) with Python {platform.python_version()}")
logger.debug(f"Importing the rest of the required modules...")

# Try to import tkinter (because Python on some platforms lacks it, especially macOS)
try:
    import tkinter as tk
    import tkinter.ttk as ttk # we don't use this right here but still worth trying to import it for error handling if it's not present
except ImportError as ie:
    logger.critical(f"Failed to import tkinter. Please check if you need a different Python distribution or maybe just need to install Tkinter. (Full: {repr(ie)})")
    exit(1) # bail lol
from PyWeMoGUIApp import PyWeMoGUIApp


if __name__ == '__main__':
    logger.debug("Setting up Tk and initializing PyWeMoGUIApp...")
    try:
        root = tk.Tk()
        app = PyWeMoGUIApp(root)
        app.root.mainloop()
    except Exception as e:
        logger.critical(f"Failed to initialize PyWeMoGUIApp: {repr(e)}\n                   {traceback.format_exc()}")
        exit(1)
else:
    logger.critical("PyWeMoGUI is not designed to be used as a module. Please run it directly instead.")
    exit(1)