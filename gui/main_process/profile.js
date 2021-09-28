const {ipcMain} = require('electron');
 
ipcMain.on('get-entity-id', (event) => {
  client.invoke("get_entity_id", function(error, res, more) {
    var success = res[0];
    var entity_id_result = res[1];
    if (success && entity_id_result != null) {
      event.reply('notify-get-entity-id-done', entity_id_result);
      client.invoke("get_entity_name", entity_id_result, function(error, res, more) {
        var success = res[0];
        var entity_name_result = res[1];
        if (success && entity_name_result != null) {
          event.reply('notify-get-entity-name-done', entity_name_result);
        }
        else {
          event.reply('notify-zget-entity-name-error', entity_name_result);
        }
      });
    }
    else {
      event.reply('notify-get-entity-id-error', entity_id_result);
    }
  });
});
