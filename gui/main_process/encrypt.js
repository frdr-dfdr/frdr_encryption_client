const {dialog, ipcMain} = require('electron')

// Main process to open a folder selector dialog
ipcMain.on('open-input-dir-dialog', function (event) {
  selected_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
  if (selected_path) {
    event.reply('selected-input-dir', selected_path)
  }
})

ipcMain.on('open-output-dir-dialog', function (event) {
  selected_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
  if (selected_path) {
    event.reply('selected-output-dir', selected_path)
  }
})