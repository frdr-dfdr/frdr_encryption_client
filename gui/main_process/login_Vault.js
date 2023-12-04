const {ipcMain} = require('electron');
const {sendMessage} = require('../main.js');

ipcMain.on('login-vault-oidc-globus', async (event, loginSuccessMsg) => {
  const { result } = await sendMessage("login_oidc_globus", [loginSuccessMsg]);
  var success = result[0];
  var errMessage = result[1];
  if (success) {
    event.reply('notify-login-oidc-done');
  }
  else {
    event.reply('notify-login-oidc-error', errMessage);
  }
});

ipcMain.on('verify-local-user-keys', async (event) => {
  const { result } = await sendMessage("verify_local_keys");
  var errMessage = result;
  if (errMessage != null) {
    event.reply('notify-verify-local-user-keys-error', errMessage);
  }
  else {
    event.reply('notify-verify-local-user-keys-done');
  }
});

ipcMain.on('sync-entity-id', (event) => {
  client.invoke("get_entity_id", function(_error, res) {
    var success_entity_id = res[0];
    var entity_id_result = res[1];
    if (success_entity_id && entity_id_result != null) {
      // Check if this id matches the vault id saved on FRDR
      client.invoke("get_user_vault_id_from_frdr", function(_event, res) {
        var success_get_vault_id_from_frdr = res[0];
        var vault_id_frdr = res[1];

        if (success_get_vault_id_from_frdr && (vault_id_frdr == null || entity_id_result != vault_id_frdr)) {
          client.invoke("send_user_vault_id_to_frdr", entity_id_result, function(_error, res) {
            var success_send_vault_id = res[0];
            if (!success_send_vault_id) {
              event.reply('notify-send-entity-id-to-frdr-error', res[1]);
            }
          });
        }
        else if (!success_get_vault_id_from_frdr) {
          event.reply('notify-get-entity-id-from-frdr-error', res[1]);
        }
      });
    }
    else {
      event.reply('notify-get-entity-id-error', entity_id_result);
    }
  });
});