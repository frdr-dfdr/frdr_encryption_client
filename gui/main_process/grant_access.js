const {dialog, ipcMain} = require('electron');
 
ipcMain.on('grant-access', (event, requester, dataset, expiryDate, dialogOptions, dialogOptions2) => {
  client.invoke("get_entity_name", requester, function(error, res, more) {
    var success = res[0];
    var result = res[1];
    if (success && result != null) {
      dialogOptions['message'] = dialogOptions['message'].replace("$1", result).replace("$2", dataset);
      const response = dialog.showMessageBoxSync(dialogOptions);
      if (response == 0) {
        const response2 = dialog.showMessageBoxSync(dialogOptions2);
        if (response2 == 0) {
          client.invoke("login_frdr_api_globus", function(error, res, more) {
            var successLogin = res[0];
            var errMessageLogin = res[1];
            if (successLogin) {
              client.invoke("grant_access", dataset, requester, expiryDate, function(error, res, more) {
                var successGrantAccess = res[0];
                var errMessageGrantAccess = res[1];
                if (successGrantAccess){
                  event.reply('notify-grant-access-done');
                } else {
                  event.reply('notify-grant-access-error', errMessageGrantAccess);
                }
              });  
            }
            else {
              event.reply('notify-login-frdr-api-error', errMessageLogin);
            }
          });         
        }
      }
    }
    else {
      event.reply('notify-get-entity-name-error', result);
    }
  });
});