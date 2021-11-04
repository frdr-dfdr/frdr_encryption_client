const {ipcMain, BrowserWindow} = require('electron');

ipcMain.on('contact-us', (_event, url) => {
  const win = new BrowserWindow({width: 800, height: 600});
  win.loadURL(url);  
});