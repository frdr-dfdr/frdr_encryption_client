const {ipcMain} = require('electron');
 
ipcMain.on('logout', (event) => {
  client.invoke("logout", function(_error, res) {
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