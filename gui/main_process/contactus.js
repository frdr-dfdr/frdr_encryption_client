const {ipcMain, BrowserWindow} = require('electron');
 
ipcMain.on('contact-us', (event) => {
  const win = new BrowserWindow({width: 800, height: 600});
  win.loadURL("https://www.frdr-dfdr.ca/repo/contactus");  
});