/*
 *   Copyright (c) 2024 Digital Research Alliance of Canada
 *  
 *   This file is part of FRDR Encryption Application.
 *  
 *   FRDR Encryption Application is free software: you can redistribute it
 *   and/or modify it under the terms of the GNU General Public License as
 *   published by the FRDR Encryption Application Software Foundation,
 *   either version 3 of the License, or (at your option) any later version.
 *  
 *   FRDR Encryption Application is distributed in the hope that it will be
 *   useful, but WITHOUT ANY WARRANTY; without even the implied
 *   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 *   PURPOSE. See the GNU General Public License for more details.
 *  
 *   You should have received a copy of the GNU General Public License
 *   along with FRDR Encryption Application. If not, see <https://www.gnu.org/licenses/>.
 */

const { app, BrowserWindow, ipcMain, dialog, shell, Menu} = require("electron");
// Does not allow a second instance
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
    app.quit();
} else {
    app.on('second-instance', (_event, _commandLine, _workingDirectory) => {
        notifier.notify({ "title": "FRDR Encryption Application", "message": "FRDR Encryption Application is already running." });
    });
}

require('update-electron-app');

const openAboutWindow = require('electron-about-window').default;

const glob = require('glob');

const zmq = require("zeromq");
sock = new zmq.Request();

const portfinder = require("portfinder");
const session = require('electron').session;

const path = require('path');
const PY_APP_GUI_FOLDER = 'app_gui';
const PY_FOLDER = '..';
const PY_MODULE = 'app_gui';

let pythonChild = null;
let mainWindow = null;

const guessPackaged = () => {
    const fullPath = path.join(__dirname, PY_APP_GUI_FOLDER)
    return require('fs').existsSync(fullPath)
};

const getScriptPath = () => {
    if (!guessPackaged()) {
        return path.join(__dirname, PY_FOLDER, PY_MODULE + '.py')
    }
    if (process.platform === 'win32') {
        return path.join(__dirname, PY_APP_GUI_FOLDER, PY_MODULE + '.exe')
    }
    return path.join(__dirname, PY_APP_GUI_FOLDER, PY_MODULE)
};

async function sendMessage(command, args) {
    await sock.send(
      JSON.stringify({
        command,
        args,
      })
    );
    let [result] = await sock.receive();
    result = JSON.parse(result.toString());
    return result;
}

module.exports = {sendMessage};

loadMainProcessJs();

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 850,
        height: 750,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    mainWindow.setMenuBarVisibility(false);

    // Load the login page by default.
    mainWindow.loadURL(require('url').format({
        pathname: path.join(__dirname, 'pages/login-FRDR.html'),
        protocol: 'file:',
        slashes: true
    }));

    // Load the login page when user is unauthenticated.
    ipcMain.on("unauthenticated", (_event) => {
        mainWindow.loadURL(require('url').format({
            pathname: path.join(__dirname, 'pages/login-FRDR.html'),
            protocol: 'file:',
            slashes: true
        }))
    });

    // Load our app when user is authenticated.
    ipcMain.on("authenticated", (_event) => {
        mainWindow.loadURL(require('url').format({
            pathname: path.join(__dirname, 'pages/home.html'),
            protocol: 'file:',
            slashes: true
        }))
    });

    // Load our app when user is authenticated.
    ipcMain.on("frdr-authenticated", (_event) => {
        mainWindow.loadURL(require('url').format({
            pathname: path.join(__dirname, 'pages/login-Vault.html'),
            protocol: 'file:',
            slashes: true
        }))
    });

    // Load an error page when user is authenticated but local keys verification fails.
    ipcMain.on("verification-failed", (_event, dialogOptions) => {
        mainWindow.loadURL(require('url').format({
            pathname: path.join(__dirname, 'pages/local-keys-error.html'),
            protocol: 'file:',
            slashes: true,
        }))
        mainWindow.webContents.on('did-finish-load', function() {
            mainWindow.show();
        });
        dialog.showMessageBox(mainWindow, dialogOptions);
    });

    mainWindow.on('close', (_event) => {
        if (mainWindow != null) {
            mainWindow.hide();
        }
        mainWindow = null
    });
}

app.on('ready', () => {
    session.defaultSession.webRequest.onBeforeSendHeaders((details, callback) => {
        details.requestHeaders["User-Agent"] = "Chrome";
        callback({ cancel: false, requestHeaders: details.requestHeaders });
    });
    createWindow();
    mainWindow.webContents.session.clearStorageData();

    const menu = Menu.buildFromTemplate([
        {
            label: 'Example',
            submenu: [
                {
                    label: 'About This App',
                    click: () =>
                        openAboutWindow({
                            icon_path: path.join(__dirname, 'resources/icon.png'),
                            copyright: '<p style="text-align:center; ">Copyright (c) 2024 Digital Research Alliance of Canada <br> Distributed under GPL-3.0-or-later license</p>',
                            package_json_dir: __dirname,
                            use_version_info: false,
                            adjust_window_size: true,
                            use_inner_html: true
                        }),
                },
                {
                    role: 'quit',
                },
            ],
        },
    ]);
    app.applicationMenu = menu;
});

portfinder.basePort = 4242;
portfinder.getPort(function(_err, port) {
    sock.connect("tcp://127.0.0.1:" + String(port));
    const createApp = () => {
        let script = getScriptPath();
        if (guessPackaged()) {
            pythonChild = require('child_process').spawn(script, [port])
        } else {
            pythonChild = require('child_process').spawn('python3', [script, port])
        }

        if (pythonChild != null) {
            console.log('Python started successfully')

            pythonChild.stdout.on('data', function(data) {
                console.log(data.toString());
            });

            pythonChild.stderr.on('data', function(data) {
                console.log(data.toString());
            });
        }
    }
    app.on('ready', createApp);
});


const exitApp = () => {
    sock.send(JSON.stringify({ command: "Exit" }));
    pythonChild.kill()
    pythonChild = null
    sock.close();
}

app.on("before-quit", () => {
    if (mainWindow != null) {
        mainWindow.close();
    }
});

app.on('will-quit', ev => {
    exitApp();
    app.quit();
})

function loadMainProcessJs() {
    const files = glob.sync(path.join(__dirname, 'main_process/*.js'))
    files.forEach((file) => { require(file) })
}