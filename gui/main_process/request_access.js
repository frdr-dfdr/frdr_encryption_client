const {dialog, ipcMain, clipboard} = require('electron');
 
ipcMain.on('request-access', (event, dialogOptions, copiedDoneDialogOptions) => {
  client.invoke("get_entity_id", function(error, res, more) {
    var success = res[0];
    var result = res[1];
    if (success) {
      dialogOptions['detail'] = result;
      const response = dialog.showMessageBoxSync(dialogOptions);
      if (response == 0) {
        clipboard.writeText(result);
        dialog.showMessageBoxSync(copiedDoneDialogOptions);
      }
    }
    else {
      event.reply('notify-request-access-error', result);
    }
  });  
});