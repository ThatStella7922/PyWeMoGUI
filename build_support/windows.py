import argparse
import logging
import os
from PyWeMoGUISystemUtils import GitUtils

class windows_prep:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

class windows_build:
    def __init__(self, args: argparse.Namespace):
        self.logger = logging.getLogger(__name__)
        self.args = args
    
    def build(self):
        # Bringup
        self.logger.info("""For a successful build on Windows, you must:
          1. Install all required modules (requirements.txt) with uv or pip or whatever
          2. Install PyInstaller and make sure it can be found in PATH (aka a proper installation)

          Once you have made sure this is done, you can start the build""")
          
        if not self.args.noconfirm:
            input("Press Enter to start build or press Ctrl+C to exit now!")
            
        # Directly call PyInstaller's main module (we get to reuse its logging as opposed to subprocessing it)
        import PyInstaller.__main__
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
        self.logger.info("Build complete check dist folder for the binary, scroll up for log")

def main():
    print(
        f"Made by 🐄 with ❤️  in 2026.\n\n"
        f"THIS FILE DOES NOT WORK ON ITS OWN!!!\n"
        f"Run build.py instead, it will automatically use this file as intended."
    )
    
if __name__ == "__main__":
    main()
