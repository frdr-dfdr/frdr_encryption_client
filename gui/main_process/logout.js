const {ipcMain, BrowserWindow} = require('electron');
 
ipcMain.on('logout', (event) => {
  var url = "https://auth.globus.org//v2/web/logout?redirect_uri=https://dev4.frdr.ca/repo/login/logged-out.jsp";
  const win = new BrowserWindow({width: 800, height: 600});
  win.loadURL(url);
  client.invoke("logout", function(error, res, more) {
    var success = res[0];
    var result = res[1];
    console.log(success);
    if (success){
      event.reply('notify-logout-done');
    } else {
      event.reply('notify-logout-error', result);
    }
  });  
});