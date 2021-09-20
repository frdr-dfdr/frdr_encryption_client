const {ipcMain, BrowserWindow} = require('electron');

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


ipcMain.on('login-vault-oidc-globus', (event, hostname, hostnamePKI) => {
  client.invoke("get_auth_url", hostname, hostnamePKI, function(error, res, more) {
    var url = res[0];
    var errMessage = res[1];
    if (url) {
      const win = new BrowserWindow({width: 800, height: 600});
      win.loadURL(url);
      client.invoke("login_oidc_temp", url, function(error, res, more) {
        var success = res[0];
        var errLoginMessage = res[1];
        if (success) {
          win.close();
          event.reply('notify-login-oidc-done');
        }
        else {
          event.reply('notify-login-oidc-error', errLoginMessage);
        }
      });
    }
    else {
      event.reply('notify-get-auth-url-error', errMessage);
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


