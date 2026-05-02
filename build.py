### pywemogui "build" script aka this shit just uses PyInstaller because i have nothing better

print("Welcome to pywemogui build script v2.0")

import os
import argparse
import logging
import platform
import subprocess
import shutil
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
parser.add_argument('--loglevel', '-l', help='Optionally define how verbose logs should be (default is INFO)', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
parser.add_argument('--logtofile', '-lf', help='Optionally specify that the logs should be directed to a file', action="store_true")
parser.add_argument('--noconfirm', '-nc', help='Skip confirmation before building (for automation?)', action='store_true')
args = parser.parse_args()

if args.logtofile:
    print("Logging to file is enabled! You will not see logs in this console window")
    logging.basicConfig(level=f"{args.loglevel}", format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%I:%M:%S%p', filename="build.log", filemode="w")
else:
    logging.basicConfig(level=f"{args.loglevel}", format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%I:%M:%S%p')
logger.info(f"Logger started, loglevel is set to {args.loglevel}")
logger.info(f"Running on {platform.system()} {platform.version()} ({platform.machine()}, {os.cpu_count()}x) with Python {platform.python_version()}")

import PyInstaller.__main__

if __name__ == "__main__":
    try:
        # Determine the OS
        match platform.system():
            case "Windows":
                # Windows build instructions and code
                logger.info("""For a successful build on Windows, you must:
                          1. Install all required modules (requirements.txt) with uv or pip or whatever
                          2. Install PyInstaller and make sure it can be found in PATH (aka a proper installation)

                          Once you have made sure this is done, you can start the build""")
                if not args.noconfirm:
                    input("Press Enter to start build or press Ctrl+C to exit now!")
                prepare_to_build
                # Directly call PyInstaller's main module (we get to reuse its logging as opposed to subprocessing it)
                PyInstaller.__main__.run([
                    '--specpath',
                    'spec',
                    '--onefile',
                    '--name',
                    'PyWeMoGUI-Windows',
                    'main.py'
                    ])
                # rename the output now
                os.rename("dist/PyWeMoGUI-Windows.exe", "dist/PyWeMoGUI-Windows-{revision}.exe".format(revision=GitUtils.get_git_revision_short_hash()))
                logger.info("Build complete check dist folder for the binary, scroll up for log")
            case "Darwin":
                # Mac OS X build instructions and code
                logger.info("Hello we are on macOS")
                if not args.noconfirm:
                    input("Press Enter to start build or press Ctrl+C to exit now!")
                #logger.info("We need to install the CPython 3.14.x macOS 10.13+ universal2 wheel for lxml!") # at https://files.pythonhosted.org/packages/03/15/d4a377b385ab693ce97b472fe0c77c2b16ec79590e688b3ccc71fba19884/lxml-6.0.2-cp314-cp314-macosx_10_13_universal2.whl
                prepare_to_build()
                # Directly call PyInstaller's main module (we get to reuse its logging as opposed to subprocessing it)
                PyInstaller.__main__.run([
                    '--specpath',
                    'spec',
                    '--onedir',
                    '--windowed',
                    '--osx-bundle-identifier',
                    'thatstel.la.pywemogui',
                    #'--target-architecture',
                    #'universal2',
                    '--name',
                    'PyWeMoGUI-Darwin',
                    'main.py'
                    ])
                #rename output now
                os.rename("dist/PyWeMoGUI-Darwin.app", "dist/PyWeMoGUI-Darwin-{revision}.app".format(revision=GitUtils.get_git_revision_short_hash()))
                logger.info("Build complete check dist folder for the binary, scroll up for log")
            ### ADD ADDITIONAL CASES FOR OTHER OSES
            case _:
                #Generic catchall for an unsupported OS
                raise NotImplementedError(f"OS '{platform.system()}' is not supported in this build script yet")
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