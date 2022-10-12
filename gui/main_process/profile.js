const {ipcMain} = require('electron');
const {sendMessage} = require('../main.js');
 
ipcMain.on('get-entity-id', async (event) => {
  const {result} = await sendMessage("get_entity_id");
  var success = result[0];
  var entity_id_result = result[1];
  if (success && entity_id_result != null) {
    event.reply('notify-get-entity-id-done', entity_id_result);
    const {result: get_entity_name_result} = await sendMessage("get_entity_name", [entity_id_result])
    var success = get_entity_name_result[0];
    var entity_name_result = get_entity_name_result[1];
    if (success && entity_name_result != null) {
      event.reply('notify-get-entity-name-done', entity_name_result);
    }
    else {
      event.reply('notify-get-entity-name-error', entity_name_result);
    }
  }
  else {
    event.reply('notify-get-entity-id-error', entity_id_result);
  }
});
