const {ipcMain} = require('electron');

ipcMain.on('login-vault-oidc-globus', (event, hostname, hostnamePKI) => {
  client.invoke("login_oidc_globus", hostname, hostnamePKI, function(error, res, more) {
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

ipcMain.on('login-frdr-api-globus', (event, baseUrl) => {
  client.invoke("login_frdr_api_globus", baseUrl, function(error, res, more) {
    var success = res[0];
    var errMessage = res[1];
    if (success) {
      event.reply('notify-login-frdr-api-done');
    }
    else {
      event.reply('notify-login-frdr-api-error', errMessage);
    }
  });
});


