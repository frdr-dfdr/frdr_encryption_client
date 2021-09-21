const {ipcMain} = require('electron');
 
ipcMain.on('get-entity-id', (event) => {
  client.invoke("get_entity_id", function(error, res, more) {
    var success = res[0];
    var result = res[1];
    if (success && result != null) {
      event.reply('notify-get-entity-id-done', result);
    }
    else {
      event.reply('notify-get-entity-id-error', result);
    }
  });
});

ipcMain.on('get-entity-name', (event, entity_id) => {
  client.invoke("get_entity_name", entity_id, function(error, res, more) {
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