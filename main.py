print("PyWeMoGUI by ThatStella7922 (https://thatstel.la)")

import argparse
import sys
import os
import traceback
import platform
import logging
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(
    prog="PyWeMoGUI",
    description="A simple GUI that lets you manage your Belkin WeMo devices.",
    )
parser.add_argument('--loglevel', '-l', help='Optionally define how verbose logs should be (default is INFO)', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
args = parser.parse_args()

is_frozen_binary = getattr(sys, 'frozen', False)

# Logger configuration and basic system info retrieval
#TODO Optional argument for logging to file
logging.basicConfig(level=f"{args.loglevel}", format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%I:%M:%S%p')
logger.info(f"Logger started, loglevel is set to {args.loglevel}")
if is_frozen_binary:
    logger.info(f"Running on {platform.system()} {platform.release()} ({platform.machine()}) as a packaged release built with Python {platform.python_version()}")
else:
    logger.info(f"Running on {platform.system()} {platform.release()} ({platform.machine()}) with Python {platform.python_version()}")
logger.debug(f"Importing the rest of the required modules...")

# Try to import tkinter (because Python on some platforms lacks it, especially macOS)
try:
    import tkinter as tk
    import tkinter.ttk as ttk # we don't use this right here but still worth trying to import it for error handling if it's not present
except ImportError as ie:
    logger.critical(f"Failed to import tkinter. Please check if you need a different Python distribution or maybe just need to install Tkinter. (Full: {repr(ie)})")
    exit(1) # bail lol

try:
    if platform.system() == "Windows":
        logger.debug("Importing hidpi_tk since we are on Windows")
        from hidpi_tk import DPIAwareTk
    from PyWeMoGUIApp import PyWeMoGUIApp
except ImportError as ie:
    logger.critical(f"Importing a required library failed! {ie}. If you are running a binary from the Releases, create a GitHub issue to report this bug. Otherwise, check your installation!")
    exit(1)

if __name__ == '__main__':
    logger.debug("Setting up Tk and initializing PyWeMoGUIApp...")
    try:
        if platform.system() == "Windows":
            root = DPIAwareTk() ### supposedly, DPIAwareTk is supposed to fallback to regular Tk if not running on Windows but it crashed on macOS so I am checking explicitly for Windows before using
        else:
            root = tk.Tk() ### not on Windows, use regular Tk (*thanks* for nothing hidpit_tk)

        app = PyWeMoGUIApp(root)
        app.root.mainloop()
    except Exception as e:
        logger.critical(f"Failed to initialize PyWeMoGUIApp: {repr(e)}\n                   {traceback.format_exc()}")
        exit(1)
else:
    logger.critical("PyWeMoGUI is not designed to be used as a module. Please run it directly instead.")
    exit(1)