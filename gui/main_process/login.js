const {ipcMain, BrowserWindow} = require('electron');

ipcMain.on('login-vault-oidc-globus', (event, hostname, hostnamePKI) => {
  client.invoke("login_oidc_globus", hostname, hostnamePKI, function(_error, res) {
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
