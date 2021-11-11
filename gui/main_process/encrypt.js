const {BrowserWindow, dialog, ipcMain, shell, app} = require('electron');
const path = require('path');
const fs = require('fs');

var basepath = app.getPath("userData");

// Main process to open a folder selector dialog
ipcMain.on('encrypt-open-input-dir-dialog', function (event) {
  var selected_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
  if (selected_path) {
    event.reply('encrypt-selected-input-dir', selected_path);
  }
})

ipcMain.on('encrypt-open-output-dir-dialog', function (event) {
  var selected_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
  if (selected_path) {
    event.reply('encrypt-selected-output-dir', selected_path);
  }
})

ipcMain.on('encrypt', (event, input_path, output_path) => {
  var childWindow = new BrowserWindow({ 
    parent: BrowserWindow.getFocusedWindow(), 
    modal: true, 
    show: false, 
    width: 400, 
    height: 200, 
    webPreferences: {
      nodeIntegration: true
    }
  });
  childWindow.loadURL(require('url').format({
    pathname: path.join(__dirname, '../pages/depositor-encrypt-in-progress.html'),
    protocol: 'file:',
    slashes: true
  }));
  childWindow.once('ready-to-show', () => {
    childWindow.show()
  });
  client.invoke("encrypt", input_path, output_path, function(_error, res) {
    var success = res[0];
    var result = res[1];
    if (result != "Terminated") {
      childWindow.close();
    }
    if (success){
      event.reply('notify-encrypt-done', result);
      shell.showItemInFolder(result);
      var currentWindow = BrowserWindow.getFocusedWindow();
      currentWindow.loadURL(require('url').format({
        pathname: path.join(__dirname, '../pages/depositor-encrypt-done.html'),
        protocol: 'file:',
        slashes: true
      }));
    
      currentWindow.once('ready-to-show', () => {
        currentWindow.show()
      });
    } else {
      event.reply('notify-encrypt-error', result);
    }
  });
});

ipcMain.on('encrypt-cancel', (event) => {
  try {
    const pid = fs.readFileSync(path.join(basepath, 'pid'), 'utf8');
    process.kill(pid);
    var currentWindow = BrowserWindow.getFocusedWindow();
    currentWindow.close();
    client.invoke("cleanup", function(_error, _res) {
    
    });
  } catch (err) {
    event.reply('notify-encrypt-cancel-error', err);
  }
});