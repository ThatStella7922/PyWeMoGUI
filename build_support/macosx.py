import argparse
import json
import logging
import sys
from pathlib import Path
from urllib.request import urlopen, urlretrieve
from delocate.fuse import fuse_wheels
from packaging.utils import parse_wheel_filename
from subprocess import Popen, PIPE, STDOUT
from PyWeMoGUISystemUtils import GitUtils

class macosx_prep:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.PIP = Path("./venv/bin/pip")
        self.logger.debug(f"PIP path set to {self.PIP}")

        self.WHEELS_DIR = Path("./wheels")
        self.WHEELS_DIR.mkdir(exist_ok=True)
        self.logger.debug(f"Wheel path set to {self.WHEELS_DIR}")

        # Syntax is "package": version, set version to None to pull latest
        #
        # Here in case clamping is needed down the line because sh*t broke
        # At least the macOS build will keep working (I don't care about W*ndows)
        self.PACKAGES = {
            "pillow": None,
            "cffi": None,
            "lxml": None,
        }
        self.logger.debug(f"Packages: {self.PACKAGES}")
        
        self.PY_TAG, self.ABI_TAG = self.current_tags()
        self.logger.debug(f"Tags: {self.PY_TAG}, {self.ABI_TAG}")
        
    def pip_force_reinstall(self, path_or_url):
        '''
        Forces a reinstall of a wheel from URL or a local path.
        
        Additionally, pipes STDOUT to logger.info for parsing as UTF-8 text. 
        '''
        process = Popen([self.PIP, "install", "--force-reinstall", str(path_or_url)], text=False, stdout=PIPE, stderr=STDOUT)
        with process.stdout:
            for line in iter(process.stdout.readline, b''):
                self.logger.info("%s", line.decode("utf-8").rstrip("\n"))
        exitcode = process.wait()
        return

    def current_tags(self):
        '''
        Return the current interpreter version and tags that are relevant
        for PyPi packages.
        '''

        # Base tag
        py_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"

        # Check for the free-threaded attribute and return
        is_free_threaded = (
            hasattr(sys, "_is_gil_enabled")
            and not sys._is_gil_enabled()
        )

        # Final check
        abi_tag = f"{py_tag}t" if is_free_threaded else py_tag

        # Return both the version and the ABI tags.
        return py_tag, abi_tag

    def pypi_release(self, package, version=None):
        '''
        Returns a loaded JSON of the specified or latest version of the passed
        package.
        '''
        
        # Check for version
        if version:
            url = f"https://pypi.org/pypi/{package}/{version}/json"
            self.logger.debug(f"Fetched {version} json for {package}")
        else:
            # Fall back to latest
            url = f"https://pypi.org/pypi/{package}/json"
            self.logger.debug(f"Fetched latest json for {package}")

        # JSON loading. Obviously
        with urlopen(url) as fp:
            return json.load(fp)

    def download(self, url):
        '''
        Self-explanatory; downloads a file from a URL.
        '''
        filename = Path(url).name

        if not Path(f"{self.WHEELS_DIR}/{filename}").exists():
            self.logger.info(f"Downloading {filename}")
            urlretrieve(url, f"{self.WHEELS_DIR}/{filename}")

        return Path(f"{self.WHEELS_DIR}/{filename}")

    def compatible_wheels(self, files):
        """
        Return wheels matching the current interpreter and ABI.
        
        Will show ALL as this is before checking OS and arches.
        """

        compatible = []

        for file in files:
            try:
                _, _, _, tags = parse_wheel_filename(file["filename"])
            except Exception:
                continue

            for tag in tags:
                if (tag.interpreter == self.PY_TAG and tag.abi == self.ABI_TAG):
                    self.logger.debug(f"Added {file['filename']} to compatible wheels")
                    compatible.append(file)
                    break

        return compatible


    def find_universal2(self, files):
        '''
        Searches for a universal2 wheel to install from a list of files.
        '''
        for file in files:
            name = file["filename"]
            # Ofc, this is limited to macosx and universal2
            if ("macosx" in name and "universal2" in name): return file
        return None


    def find_arch_pair(self, files):
        '''
        Searches for x86_64 and arm64 builds of the wheel to be merged from
        a list of files.
        '''
        # Variables
        x86 = None
        arm = None

        # Iterate and check naming
        for file in files:
            name = file["filename"]

            # x86_64
            if ("macosx" in name and "x86_64.whl" in name and "universal2" not in name):
                self.logger.info(f"Found {name} as x86_64 package")
                x86 = file
            # Try arm64 next
            elif ("macosx" in name and "arm64.whl" in name and "universal2" not in name):
                self.logger.info(f"Found {name} as arm64 package")
                arm = file

        # Crashout #1
        if not x86: raise RuntimeError("No matching x86_64 wheel found")

        # Crashout #2
        if not arm: raise RuntimeError("No matching arm64 wheel found")

        # All good
        return x86, arm


    def merge_and_install(self, package, version=None):
        '''
        The actual guts of this class. Performs a search for
        the package (at version if desired), tries to find a 
        universal2 build and installs it, or falls back to 
        manually creating one.
        '''
        # Pretty
        self.logger.info(f"Grabbing universal2 {package}")

        # Get release specified or try latest, see above
        release = self.pypi_release(package, version)

        # Clamp down to files compatible with this Python version
        files = self.compatible_wheels(
            # Holy line
            [files for files in release["urls"] if files["packagetype"] == "bdist_wheel"]
        )

        # Try to find a universal2 copy of the wheel
        # They don't get pulled in automatically so this could
        # actually just be a pip moment
        universal = self.find_universal2(files)

        # Hey we found it!
        if universal:
            self.logger.info(f"Using universal2 wheel: {universal['filename']}")

            # Install the wheel and end here
            self.logger.debug(f"Forcing reinstall of {package} using pip and universal2 .whl")
            

            self.pip_force_reinstall(universal["url"])
            return
        
        self.logger.info(f"No universal2 wheel found for {package}, falling back to merging")

        # Time to merge, find the matching packages
        x86, arm = self.find_arch_pair(files)

        self.logger.info("Merging wheels:")
        self.logger.info(f"  {x86['filename']}")
        self.logger.info(f"  {arm['filename']}")

        # Download the split packages
        x86_path = self.download(x86["url"])
        arm_path = self.download(arm["url"])

        # Merge the wheels
        created = fuse_wheels(
            str(x86_path),
            str(arm_path),
            str(self.WHEELS_DIR),
        )

        # Check if the output path exists to consider this a success.
        if not created.exists():
            raise RuntimeError(f"The output {created} wasn't made.")

        self.logger.info(f"Created {created.name}")
        
        # Install the merged wheel
        self.logger.debug(f"Forcing reinstall of {package} using pip and generated .whl")
        self.pip_force_reinstall(created)

class macosx_build:
    def __init__(self, args: argparse.Namespace):
        self.logger = logging.getLogger(__name__)
        self.args = args
    
    def build(self):
        # Bringup
        self.logger.info("Hello we are on macOS")
        if not self.args.noconfirm:
            input("Press Enter to start build or press Ctrl+C to exit now!")
            
        # Create prep class
        prep = macosx_prep()
        
        # Check universal2 and skipmerge statuses
        if self.args.universal2 and not self.args.skipmerge:
            self.logger.info("In order to build universal2, we need to download and merge a few packages.")
            # Download and/or merge universal2 wheels
            for package, version in prep.PACKAGES.items():
                prep.merge_and_install(package, version)
        elif self.args.universal2 and self.args.skipmerge:
            self.logger.info("Building universal2 and skipping wheel preperation. This will fail if you don't have universal2 wheels!")
        else:
            self.logger.info("Building for current architecture. To build universal2, pass --universal2 or -u2 to this script.")
            
        # Directly call PyInstaller's main module (we get to reuse its logging as opposed to subprocessing it)
        import PyInstaller.__main__
        PyInstaller.__main__.run([
            '--specpath',
            'spec',
            '--onedir',
            '--windowed',
            '--osx-bundle-identifier',
            'thatstel.la.pywemogui',
            *(
                ['--target-architecture', 'universal2']
                if self.args.universal2
                else []
            ),
            '--name',
            'PyWeMoGUI-Darwin',
            'main.py'
            ])
                
        # Rename output
        os.rename("dist/PyWeMoGUI-Darwin.app", "dist/PyWeMoGUI-Darwin-{revision}.app".format(revision=GitUtils.get_git_revision_short_hash()))
        
        # Success
        self.logger.info("Build complete check dist folder for the binary, scroll up for log")
    
def main():
    print(
        f"Made by 🐄 with ❤️  in 2026.\n\n"
        f"THIS FILE DOES NOT WORK ON ITS OWN!!!\n"
        f"Run build.py instead, it will automatically use this file as intended."
    )
    
if __name__ == "__main__":
    main()
