const {dialog, ipcMain} = require('electron');
 
ipcMain.on('grant-access', (event, requester, dataset, expiryDate, dialogOptions, dialogOptions2, loginSuccessMsg) => {
  client.invoke("get_request_info", requester, dataset, function(_error, res) {
    var entity_success = res[0];
    var entity_result = res[1];
    var dataset_success = res[2];
    var dataset_result = res[3];
    if (entity_success && entity_result != null && dataset_success) {
      dialogOptions['message'] = dialogOptions['message'].replace("$1", entity_result).replace("$2", dataset_result);
      const response = dialog.showMessageBoxSync(dialogOptions);
      if (response == 0) {
        const response2 = dialog.showMessageBoxSync(dialogOptions2);
        if (response2 == 0) {
          client.invoke("login_frdr_api_globus", loginSuccessMsg, function(_error, res) {
            var successLogin = res[0];
            var errMessageLogin = res[1];
            if (successLogin) {
              client.invoke("grant_access", dataset, requester, expiryDate, function(_error, res) {
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
    else if (!entity_success || entity_result == null){
      event.reply('notify-get-entity-name-error', entity_result);
    }
    else if (!dataset_success){
      event.reply('notify-get-dataset-title-error', dataset_result);
    }
  });
});