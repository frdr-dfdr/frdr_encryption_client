const {ipcMain} = require('electron');

ipcMain.on('login-frdr-api-globus', (event, loginSuccessMsg) => {
  client.invoke("login_frdr_api_globus", loginSuccessMsg, function(_error, res) {
    var successLogin = res[0];
    var errMessageLogin = res[1];
    if (successLogin) {
      console.log("done");
      event.reply('notify-login-frdr-done');
    }
    else {
      event.reply('notify-login-frdr-error', errMessageLogin);
    }
  });
});