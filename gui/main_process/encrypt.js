const {BrowserWindow, dialog, ipcMain, shell} = require('electron');
const path = require('path');
 
// Main process to open a folder selector dialog
ipcMain.on('open-input-dir-dialog', function (event) {
  selected_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
  if (selected_path) {
    event.reply('selected-input-dir', selected_path);
  }
})

ipcMain.on('open-output-dir-dialog', function (event) {
  selected_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
  if (selected_path) {
    event.reply('selected-output-dir', selected_path);
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
  client.invoke("encrypt", input_path, output_path, function(error, res, more) {
    childWindow.close();
    var success = res[0];
    var result = res[1];
    if (success){
      event.reply('notify-encrypt-done', result);
      shell.showItemInFolder(result);
    } else {
      event.reply('notify-encrypt-error', result);
    }
  });
});