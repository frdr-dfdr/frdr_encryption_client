const {ipcMain} = require('electron');

ipcMain.on('login-vault-oidc-globus', (event, loginSuccessMsg) => {
  client.invoke("login_oidc_globus", loginSuccessMsg, function(_error, res) {
    var success = res[0];
    var errMessage = res[1];
    if (success) {
      event.reply('notify-login-oidc-done');
    }
    else {
      event.reply('notify-login-oidc-error', errMessage);
    }
  });
});

ipcMain.on('verify-local-user-keys', (event) => {
  client.invoke("verify_local_keys", function(_error, res) {
    var errMessage = res;
    if (errMessage != null) {
      event.reply('notify-verify-local-user-keys-error', errMessage);
    }
    else {
      event.reply('notify-verify-local-user-keys-done');
    }
  });
});