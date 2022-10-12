const {ipcMain} = require('electron');
const {sendMessage} = require('../main.js');

ipcMain.on('login-vault-oidc-globus', async (event, loginSuccessMsg) => {
  const { result } = await sendMessage("login_oidc_globus", [loginSuccessMsg]);
  var success = result[0];
  var errMessage = result[1];
  if (success) {
    event.reply('notify-login-oidc-done');
  }
  else {
    event.reply('notify-login-oidc-error', errMessage);
  }
});

ipcMain.on('verify-local-user-keys', async (event) => {
  const { result } = await sendMessage("verify_local_keys");
  var errMessage = result;
  if (errMessage != null) {
    event.reply('notify-verify-local-user-keys-error', errMessage);
  }
  else {
    event.reply('notify-verify-local-user-keys-done');
  }
});