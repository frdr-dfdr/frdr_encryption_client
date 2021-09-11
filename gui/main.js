const time1 = new Date().getTime();

if(require('electron-squirrel-startup')) return;
const {app, Menu, BrowserWindow, ipcMain, shell} = require("electron");
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
const glob = require('glob');
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
const PY_APP_GUI_FOLDER = 'app_gui'
const PY_FOLDER = '..'
const PY_MODULE = 'app_gui'

let pythonChild = null
let mainWindow = null
let input_path = null;
let selected_path = null;
let $ = require('jquery');

//TODO: this is for?
const sleep = (waitTimeInMs) => new Promise(resolve => setTimeout(resolve, waitTimeInMs));

const guessPackaged = () => {
  const fullPath = path.join(__dirname, PY_APP_GUI_FOLDER)
  return require('fs').existsSync(fullPath)
}

const getScriptPath = () => {
  if (!guessPackaged()) {
    return path.join(__dirname, PY_FOLDER, PY_MODULE + '.py')
  }
  if (process.platform === 'win32') {
    return path.join(__dirname, PY_APP_GUI_FOLDER, PY_MODULE + '.exe')
  }
  return path.join(__dirname, PY_APP_GUI_FOLDER, PY_MODULE)
}

loadMainProcessJs();

function createWindow(){
  mainWindow = new BrowserWindow({
    width: 800,
    height: 628,
    webPreferences: {
      nodeIntegration: true,
      enableRemoteModule: true
    }
  });

  mainWindow.setMenuBarVisibility(false);

  // Load the login page by default.
  mainWindow.loadURL(require('url').format({
    pathname: path.join(__dirname, 'pages/login.html'),
    protocol: 'file:',
    slashes: true
  }))

  // Load the login page when user is unauthenticated.
  ipcMain.on("unauthenticated", (event) => {
    mainWindow.loadURL(require('url').format({
      pathname: path.join(__dirname, 'pages/login.html'),
      protocol: 'file:',
      slashes: true
    }))
  })

  // Load our app when user is authenticated.
  ipcMain.on("authenticated", async event => {
    mainWindow.loadURL(require('url').format({
      pathname: path.join(__dirname, 'pages/home.html'),
      protocol: 'file:',
      slashes: true
    }))
  })

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
  const createApp = () => {
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
  app.on('ready', createApp);
});

ipcMain.on("load-end", () => {
  let time2 = new Date().getTime();
  let time = time2 - time1;
  console.log("launch in :" + time + "ms");
});

const exitApp = () => {
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
  exitApp();
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

// // Main process to open a file/folder selector dialog
// const ipc = require('electron').ipcMain
// ipc.on('open-file-dialog', function (event) {
//   input_path = dialog.showOpenDialogSync({properties: ['openFile']});
//   if (input_path) {
//     client.invoke("set_input_path", input_path[0], function(error, res, more) {} );
//     event.reply('selected-file', input_path)
//   }
// })

// ipc.on('open-input-dir-dialog', function (event) {
//   selected_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
//   if (selected_path) {
//     event.reply('selected-input-dir', selected_path)
//   }
// })

// ipc.on('open-output-dir-dialog', function (event) {
//   selected_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
//   if (selected_path) {
//     event.reply('selected-output-dir', selected_path)
//   }
// })

function loadMainProcessJs () {
  const files = glob.sync(path.join(__dirname, 'main_process/*.js'))
  files.forEach((file) => { require(file) })
}

ipcMain.on('encrypt', (event, input_path, output_path) => {
  var childWindow = new BrowserWindow({ 
    parent: mainWindow, 
    modal: true, 
    show: false, 
    width: 400, 
    height: 200, 
    webPreferences: {
      nodeIntegration: true
    }
  });
  childWindow.loadURL(require('url').format({
    pathname: path.join(__dirname, 'pages/depositor-encrypt-in-progress.html'),
    protocol: 'file:',
    slashes: true
  }));
  childWindow.once('ready-to-show', () => {
    childWindow.show()
  });
  console.log(input_path);
  client.invoke("encrypt", input_path, output_path, function(error, res, more) {
    var success = res[0];
    var result = res[1];
    childWindow.close();
    if (success){
      // TODO: add a pop up window for notification
      notifier.notify({"title" : $.i18n('app-name'), "message" : $.i18n('app-depositor-encrypt-done', result)});
      shell.showItemInFolder(result);
    } else {
      // TODO: add a pop up window for notification
      notifier.notify({"title" : $.i18n('app-name'), "message" : $.i18n('app-depositor-encrypt-error', result)});
    }
  });
});