const {BrowserWindow, dialog, ipcMain} = require('electron');
const path = require('path');
const {sendMessage} = require('../main.js');

ipcMain.on('grant-access', async(event, requester, dataset, dialogOptions) => {
  const {result} = await sendMessage("get_request_info", [requester, dataset]);
  var entity_success = result[0];
  var entity_result = result[1];
  var dataset_success = result[2];
  var dataset_result = result[3];
  if (entity_success && entity_result != null && dataset_success) {
    dialogOptions['message'] = dialogOptions['message'].replace("$1", entity_result).replace("$2", dataset_result);
    const response = dialog.showMessageBoxSync(dialogOptions);
    if (response == 0) {
      const {result: grant_access_result} = await sendMessage("grant_access", [dataset, requester])
      var successGrantAccess = grant_access_result[0];
      var errMessageGrantAccess = grant_access_result[1];
      if (successGrantAccess){
        event.reply('notify-grant-access-done');
      } else {
        event.reply('notify-grant-access-error', errMessageGrantAccess);
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

ipcMain.on('grant-access-done-show-next-step', (_event) => {
  var currentWindow = BrowserWindow.getFocusedWindow();
  currentWindow.loadURL(require('url').format({
    pathname: path.join(__dirname, '../pages/grant-access-done.html'),
    protocol: 'file:',
    slashes: true
  }));

  currentWindow.once('ready-to-show', () => {
    currentWindow.show()
  });
});