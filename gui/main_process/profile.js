const {ipcMain} = require('electron');
 
ipcMain.on('get-entity-id', (event) => {
  client.invoke("get_entity_id", function(_error, res) {
    var success = res[0];
    var entity_id_result = res[1];
    if (success && entity_id_result != null) {
      event.reply('notify-get-entity-id-done', entity_id_result);

      // Check if this id matches the vault id saved on FRDR
      client.invoke("get_user_vault_id_from_frdr", function(_event, res) {
        var success = res[0];
        var vault_id_frdr = res[1];
        if (!success || vault_id_frdr == null || entity_id_result != vault_id_frdr) {
          event.reply('notify-enable-send-button');
        }
      });

      client.invoke("get_entity_name", entity_id_result, function(_error, res) {
        var success = res[0];
        var entity_name_result = res[1];
        if (success && entity_name_result != null) {
          event.reply('notify-get-entity-name-done', entity_name_result);
        }
        else {
          event.reply('notify-get-entity-name-error', entity_name_result);
        }
      });
    }
    else {
      event.reply('notify-get-entity-id-error', entity_id_result);
    }
  });
});


ipcMain.on('send_user_vault_id_to_frdr', (event, vaultId) => {
  client.invoke("send_user_vault_id_to_frdr", vaultId, function(_error, res) {
    var success = res[0];
    if (success) {
      event.reply('notify-send-vault-id-done');
    }
    else {
      event.reply('notify-get-entity-id-error', res[1]);
    }
  });
});