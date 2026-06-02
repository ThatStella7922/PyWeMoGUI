### pywemogui "build" script aka this shit just uses PyInstaller because i have nothing better

print("Welcome to pywemogui build script v2.0")

import os
import argparse
import logging
import platform
import subprocess
import shutil
from build_support.windows import windows_build
from build_support.macosx import macosx_build
from PyWeMoGUISystemUtils import GitUtils

def clean_build_folder():
    '''
    Utility to delete the build and dist folders in the current dir
    
    It will not ask before deleting so keep that in mind
    '''
    if os.path.exists("build"):
        shutil.rmtree("build")
        logger.debug("Removed build folder")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        logger.debug("Removed dist folder")

def prepare_to_build():
    '''
    Utility to prepare for a build, includes logging.
    
    Cleans build folder and logs some stuff for now
    '''
    logger.info("Preparing to build (cleaning build folder)")
    clean_build_folder()
    logger.info("Now starting the build please WAIT")

# Create argument parser and define the options
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(
    prog="PyWeMoGUI Build Script",
    description="Build packaged binaries of PyWeMoGUI",
    )

# General
parser.add_argument('--loglevel', '-l', help='Optionally define how verbose logs should be (default is INFO)', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
parser.add_argument('--logtofile', '-lf', help='Optionally specify that the logs should be directed to a file', action="store_true")
parser.add_argument('--noconfirm', '-nc', help='Skip confirmation before building (for automation?)', action='store_true')

# macosx-specific
parser.add_argument('--universal2', '-u2', help='Enables building one binary for both Intel-based Macs and Macs with Apple silicon', action='store_true')
parser.add_argument('--skipmerge', '-sm', help='Skips downloading and creating universal2 wheels.', action='store_true')

# parser
args = parser.parse_args()

if args.logtofile:
    print("Logging to file is enabled! You will not see logs in this console window")
    logging.basicConfig(level=f"{args.loglevel}", format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%I:%M:%S%p', filename="build.log", filemode="w")
else:
    logging.basicConfig(level=f"{args.loglevel}", format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%I:%M:%S%p')
logger.info(f"Logger started, loglevel is set to {args.loglevel}")
logger.info(f"Running on {platform.system()} {platform.version()} ({platform.machine()}, {os.cpu_count()}x) with Python {platform.python_version()}")

if __name__ == "__main__":
    try:
        prepare_to_build()
        # Determine the OS
        match platform.system():
            case "Windows":
                buildsupport = windows_build(args)
            case "Darwin":
                buildsupport = macosx_build(args)
            ### ADD ADDITIONAL CASES FOR OTHER OSES
            case _:
                #Generic catchall for an unsupported OS
                raise NotImplementedError(f"OS '{platform.system()}' is not supported in this build script yet")
                
        buildsupport.build()
    #Error handling
    except NotImplementedError as nie:
        #We use NotImplementedError for when an OS is unsupported
        logger.critical(f"{nie}")
    except Exception as e:
        logger.critical(f"Something broke so badly that there isn't a dedicated exception handler for it")
        logger.critical(f"Full error: {repr(e)}")
    except KeyboardInterrupt:
        #Make breaking with ctrl+c a bit nicer
        print("\n")
        logger.info("Ctrl+C caught, exiting...")
        exit(1)
