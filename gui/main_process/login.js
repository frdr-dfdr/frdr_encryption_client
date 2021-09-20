const {ipcMain} = require('electron');

ipcMain.on('login', (event, hostname, hostnamePKI) => {
  client.invoke("login_oidc_globus", hostname, hostnamePKI, function(error, res, more) {
    var success = res[0];
    var errMessage = res[1];
    if (success) {
      event.reply('notify-login-done');
    }
    else {
      event.reply('notify-login-error', errMessage);
    }
  });
});
