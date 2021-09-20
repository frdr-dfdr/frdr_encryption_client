const {dialog, ipcMain} = require('electron');
 
ipcMain.on('get-entity-name', (event, requester) => {
  client.invoke("get_entity_name", requester, function(error, res, more) {
    var success = res[0];
    var result = res[1];
    if (success && result != null) {
      event.reply('notify-get-entity-name-done', result);
    }
    else {
      event.reply('notify-zget-entity-name-error', result);
    }
  });
});

ipcMain.on('grant-access', (event, dataset, requester, expiryDate, dialogOptions) => {
  const response = dialog.showMessageBoxSync(dialogOptions);

  if (response == 0) {
    client.invoke("grant_access", dataset, requester, expiryDate, function(error, res, more) {
      var success = res[0];
      var errMessage = res[1];
      if (success){
        event.reply('notify-grant-access-done');
      } else {
        event.reply('notify-grant-access-error', errMessage);
      }
    });
  }
});