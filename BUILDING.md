# FRDR Encryption Application

## Building 

The Python code needs to be built on its target platform using `pyinstaller`:

(Install `pyinstaller` if not installed: `pip install pyinstaller`)

`pyinstaller -w app_gui.py --distpath gui --add-data './config/config.yml:./config'` (Windows)

`pyinstaller -w app_gui.py --distpath gui --add-data './config/config.yml:./config'` (Mac)

We need to include the config file when generating the bundle.

(On Mac, this also builds a .app version of the Python code, which you'll actually want to delete -- just keep the folder of CLI tools. Run this command: `rm -rf ./gui/app_gui.app/`)

### Build for Development

#### MacOS 

After building the python code, the GUI can be built from the `gui` subdirectory with `electron-packager`:

(Install `electron-packager` if not installed: `npm install --save-dev @electron/packager`)

`electron-packager . --icon=resources/icon.icns`

To build for development on Mac, don't need to create a new key and can ad-hoc code sign:

`cd FRDR\ Encryption-darwin-x64/ && codesign --deep --force --verbose --sign - FRDR\ Encryption.app/`

To package for install:

`hdiutil create tmp.dmg -ov -volname "FRDREncryptionApplication" -fs HFS+ -srcfolder frdr-encryption-application-darwin-x64/ && hdiutil convert tmp.dmg -format UDZO -o FRDREncryptionApplication.dmg && rm tmp.dmg` (Mac)

#### Windows

##### Option 1: build with `electron-packager`
After building the python code, the GUI can be built from the `gui` subdirectory with `electron-packager`:

(Install `electron-packager` if not installed: `npm install --save-dev @electron/packager`)

`electron-packager . --icon=resources/icon.ico`

To package for install:
`electron-installer-windows --src frdr-encryption-application-win32-x64/ --dest install/ --config config.json`

##### Option 2: build with `electron-builder`

Remove `"sign": "./windowsSign.js"` from the package.json file, and run command: 

`npm run dist`

### Build and Sign for Distribution

#### Mac

##### Method 1: Use electron-builder

Change `teamId` in the package.json file, and run the command to package, sign and notarize the app.

`APPLE_ID=[DEVELOPER APPLE ID] APPLE_APP_SPECIFIC_PASSWORD=[APP SPECIFIC PASSWORD] APPLE_TEAM_ID=[DEVELOPER TEAM ID] npm run dist`

##### Method 2: Use @electron/osx-sign and @electron/notarize
After building the python code, the GUI can be built from the `gui` subdirectory with `electron-packager`:

`electron-packager . --icon=resources/icon.icns --asar --extra-resource=app_gui`

On Mac, you can sign for distribution with `electron-osx-sign` and `electron-notarize-cli`, and you need to include the embedded Python binaries:

`IFS=$'\n' && electron-osx-sign FRDR\ Encryption-darwin-x64/FRDR\ Encryption.app/ $(find FRDR\ Encryption-darwin-x64/FRDR\ Encryption.app/Contents/ -type f -perm -u+x) --identity='[DISTRIBUTION CERTIFICATE COMMON NAME]' --entitlements=entitlements.plist --entitlements-inherit=entitlements.plist --hardenedRuntime`

`APPLE_ID=[DEVELOPER APPLE ID] APPLE_APP_SPECIFIC_PASSWORD=[APP SPECIFIC PASSWORD] APPLE_TEAM_ID=[APPLE DEVELOPER TEAM ID] node ../codesign_scripts/notarize.js`

#### Windows
Set the path to your Host and client authentication certificate in SMCTL:

```
set SM_HOST=<host URL>
set SM_CLIENT_CERT_FILE=<P12 client authentication certificate file path>
```

Run the command to build the app, make sure `"sign": "./windowsSign.js"` is included in the package.json file to sign the binaries. 

`npm run dist`

### Troubleshooting on Windows
If found the following error on Windows, Requests is not working in PyInstaller packages because of missing file from charset_normalizer module.
```
Traceback (most recent call last):
  File "requests\compat.py", line 11, in <module>
ModuleNotFoundError: No module named 'chardet'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "app_gui.py", line 28, in <module>
  File "PyInstaller\loader\pyimod03_importers.py", line 546, in exec_module
  File "modules\EncryptionClient.py", line 22, in <module>
  File "PyInstaller\loader\pyimod03_importers.py", line 546, in exec_module
  File "hvac\__init__.py", line 1, in <module>
  File "PyInstaller\loader\pyimod03_importers.py", line 546, in exec_module
  File "hvac\v1\__init__.py", line 3, in <module>
  File "PyInstaller\loader\pyimod03_importers.py", line 546, in exec_module
  File "hvac\adapters.py", line 7, in <module>
  File "PyInstaller\loader\pyimod03_importers.py", line 546, in exec_module
  File "requests\__init__.py", line 45, in <module>
  File "PyInstaller\loader\pyimod03_importers.py", line 546, in exec_module
  File "requests\exceptions.py", line 9, in <module>
  File "PyInstaller\loader\pyimod03_importers.py", line 546, in exec_module
  File "requests\compat.py", line 13, in <module>
  File "PyInstaller\loader\pyimod03_importers.py", line 546, in exec_module
  File "charset_normalizer\__init__.py", line 24, in <module>
  File "PyInstaller\loader\pyimod03_importers.py", line 546, in exec_module
  File "charset_normalizer\api.py", line 5, in <module>
  File "PyInstaller\loader\pyimod03_importers.py", line 546, in exec_module
  File "charset_normalizer\cd.py", line 14, in <module>
ModuleNotFoundError: No module named 'charset_normalizer.md__mypyc'
``` 
Run `pyinstaller -w app_gui.py --distpath gui --add-data './config/config.yml;./config' --hiddenimport charset_normalizer.md__mypyc` or upgrade pyinstaller `pip install pyinstaller==5.10.1` and install hooks repo `pip install "pyinstaller-hooks-contrib>=2022.15"`.

## Upgrade Dependencies

### Upgrade Python Packages
Upgrade packages and update requirements.txt or requirements_windows.txt.
```
pip-upgrade (Mac)
pip-upgrade .\requirements_windows.txt (Windows)
```

### Update Electron App Dependencies
Upgrade dependencies in package.json and update it.
```
cd gui

## install npm-check-updates if needed
npm install -g npm-check-updates

ncu -u
npm install
```
