"use strict";

if(require('electron-squirrel-startup')) return;
const {app, dialog, Menu, BrowserWindow} = require("electron");
// Does not allow a second instance
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    notifier.notify({"title" : "FRDR Encryption Application", "message" : "FRDR Encryption Application is already running."});
  });
}

require('update-electron-app')();
const notifier = require("node-notifier");
const zerorpc = require("zerorpc");
const constLargeEnoughHeartbeat = 1000 * 60 * 60 * 2 // 2 hour in ms
const clientOptions = {
  "heartbeatInterval": constLargeEnoughHeartbeat,
  "timeout": 60 * 60 * 2
}
global.client = new zerorpc.Client(clientOptions)
const portfinder = require("portfinder");
const session = require('electron').session;

const path = require('path')
const PY_CRYPTO_GUI_FOLDER = 'crypto_gui'
const PY_FOLDER = '..'
const PY_MODULE = 'crypto_gui'

let pythonChild = null
let mainWindow = null
//TODO: Add about window?
let aboutWindow = null
let input_path = null;

//TODO: this is for?
const sleep = (waitTimeInMs) => new Promise(resolve => setTimeout(resolve, waitTimeInMs));

const guessPackaged = () => {
  const fullPath = path.join(__dirname, PY_CRYPTO_GUI_FOLDER)
  return require('fs').existsSync(fullPath)
}

const getScriptPath = () => {
  if (!guessPackaged()) {
    return path.join(__dirname, PY_FOLDER, PY_MODULE + '.py')
  }
  if (process.platform === 'win32') {
    return path.join(__dirname, PY_CRYPTO_GUI_FOLDER, PY_MODULE + '.exe')
  }
  return path.join(__dirname, PY_CRYPTO_GUI_FOLDER, PY_MODULE)
}

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 530,
    height: 750,
    backgroundColor: "#D6D8DC",
    webPreferences: {
      nodeIntegration: true,
      enableRemoteModule: true
    }
  });

  mainWindow.setMenuBarVisibility(false);

  mainWindow.loadURL(require('url').format({
    pathname: path.join(__dirname, 'indexMain.html'),
    protocol: 'file:',
    slashes: true
  }))

  mainWindow.on('close', (event) => {
    if (mainWindow != null){
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
})

portfinder.basePort = 4242;
let port = portfinder.getPort(function (err, port) {
  client.connect("tcp://127.0.0.1:" + String(port));
  const createCrypto = () => {
    let script = getScriptPath()
    if (guessPackaged()) {
      pythonChild = require('child_process').spawn(script, [port])
    } else {
      pythonChild = require('child_process').spawn('python3', [script, port])
    }

    if (pythonChild != null) {
      console.log('Python started successfully')

      pythonChild.stdout.on('data', function (data) {
        console.log(data.toString());
      });

      pythonChild.stderr.on('data', function (data) {
        console.log(data.toString());
      });
    }
  }
  app.on('ready', createCrypto);
});

const exitCrypto = () => {
  pythonChild.kill()
  pythonChild = null
  global.client.close();
}

app.on("before-quit", ev => {
  if (mainWindow != null){
    mainWindow.close();
  }
  top = null;
});

app.on('will-quit', ev => {
  exitCrypto();
  app.quit();
})


if (process.argv.slice(-1)[0] === '--run-tests') {
  sleep(2000).then(() => {
    const total_tests = 1
    let tests_passing = 0
    let failed_tests = []

    if (pythonChild != null) {
      tests_passing++;
    } else {
      failed_tests.push('spawn_python');
    }

    console.log(`of ${total_tests} tests, ${tests_passing} passing`);

    if (tests_passing < total_tests) {
      console.error(`failed tests: ${failed_tests}`);  
    }

    app.quit();
  });
};

let top = {};

// Main process to open a file/folder selector dialog
const ipc = require('electron').ipcMain
ipc.on('open-file-dialog', function (event) {
  input_path = dialog.showOpenDialogSync({properties: ['openFile']});
  if (input_path) {
    client.invoke("set_input_path", input_path[0], function(error, res, more) {} );
    event.reply('selected-file', input_path)
  }
})

ipc.on('open-dir-dialog', function (event) {
  input_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
  if (input_path) {
    client.invoke("set_input_path", input_path[0], function(error, res, more) {} );
    event.reply('selected-dir', input_path)
  }
})