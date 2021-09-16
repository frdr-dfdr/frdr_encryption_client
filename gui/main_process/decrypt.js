const {BrowserWindow, dialog, ipcMain} = require('electron');
const path = require('path');

// Main process to open a file or folder selector dialog
ipcMain.on('open-file-dialog', function (event) {
  input_path = dialog.showOpenDialogSync({properties: ['openFile']});
  if (input_path) {
    event.reply('selected-file', input_path);
  }
})

ipcMain.on('open-output-dir-dialog', function (event) {
  selected_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
  if (selected_path) {
    event.reply('selected-output-dir', selected_path);
  }
})

ipcMain.on('decrypt', (event, input_path, output_path, url) => {
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
    pathname: path.join(__dirname, '../pages/requester-decrypt-in-progress.html'),
    protocol: 'file:',
    slashes: true
  }));

  childWindow.once('ready-to-show', () => {
    childWindow.show()
  });

  client.invoke("decrypt", input_path, output_path, url, function(error, res, more) {
    childWindow.close();
    var success = res[0];
    var errMessage = res[1];
    if (success){
      event.reply('notify-decrypt-done');
    } else {
      event.reply('notify-decrypt-error', errMessage);
    }
  });
});