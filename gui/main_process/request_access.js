const {dialog, ipcMain, clipboard} = require('electron');
const {sendMessage} = require('../main.js');

ipcMain.on('request-access', async (event, dialogOptions, copiedDoneDialogOptions) => {
  const {result} = await sendMessage("get_entity_id");
  var success = result[0];
  var message = result[1];
  if (success) {
    dialogOptions['detail'] = message;
    const response = dialog.showMessageBoxSync(dialogOptions);
    if (response == 0) {
      clipboard.writeText(message);
      dialog.showMessageBoxSync(copiedDoneDialogOptions);
    }
  }
  else {
    event.reply('notify-request-access-error', message);
  }
});