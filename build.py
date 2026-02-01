### pywemogui "build" script aka this shit just uses PyInstaller because i have nothing better

from os import name
import os
import subprocess
import shutil

def determine_os():
    if name == "nt":
        return "windows"
    elif name == "darwin":
        return "macos"
    elif name == "posix":
        return "linux"
    else:
        return "unknown"

if __name__ == "__main__":
    print("Welcome to pywemogui build script v1.0")
    print(f"Detected OS: {determine_os()}. Build requires PyInstaller and PyWeMo")
    match determine_os():
        case "windows":
            print("Build will begin when you press any key")
            os.system('pause')
            print("Preparing to build (cleaning build folder)")
            if os.path.exists("build"):
                shutil.rmtree("build")
            if os.path.exists("dist"):
                shutil.rmtree("dist")
            print("Building please WAIT")
            result = subprocess.run(['pyinstaller', '-F', 'main.py'], capture_output=True, text=True)
            log = result.stdout.strip()
            with open("build.log", "w") as log_file:
                log_file.write(log)
            log_file.close()
            print("Build complete check dist folder for the binary or build.log for build log")
        case _:
            raise NotImplementedError("Build script only supports Windows")