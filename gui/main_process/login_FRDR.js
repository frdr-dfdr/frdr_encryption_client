const {ipcMain} = require('electron');
const {sendMessage} = require('../main.js');

ipcMain.on('login-frdr-api-globus', async (event, loginSuccessMsg) => {
  const { result } = await sendMessage("login_frdr_api_globus", [loginSuccessMsg]);
  var successLogin = result[0];
  var errMessageLogin = result[1];
  if (successLogin) {
    event.reply('notify-login-frdr-done');
  }
  else {
    event.reply('notify-login-frdr-error', errMessageLogin);
  }
});