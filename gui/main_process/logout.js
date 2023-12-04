const {ipcMain} = require('electron');
const {sendMessage} = require('../main.js');
 
ipcMain.on('logout', async (event) => {
  const {result} = await sendMessage("logout");
  var success = result[0];
  var error = result[1];
  if (success){
    event.reply('notify-logout-done');
  } else {
    event.reply('notify-logout-error', error);
  }
});