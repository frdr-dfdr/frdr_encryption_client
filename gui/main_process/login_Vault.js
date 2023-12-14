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

ipcMain.on('sync-entity-id', async (event) => {
  const { result } = await sendMessage("get_entity_id");
  var success_entity_id = result[0];
  var entity_id_result = result[1];
  if (success_entity_id && entity_id_result != null) {
    // Check if this id matches the vault id saved on FRDR
    const {result: get_user_vault_id_from_frdr_result} = await sendMessage("get_user_vault_id_from_frdr");
    var success_get_vault_id_from_frdr = get_user_vault_id_from_frdr_result[0];
    var vault_id_frdr = get_user_vault_id_from_frdr_result[1];
    if (success_get_vault_id_from_frdr && (vault_id_frdr == null || entity_id_result != vault_id_frdr)) {
      const {result: send_user_vault_id_to_frdr_result } = await sendMessage("send_user_vault_id_to_frdr", [entity_id_result]);
      var success_send_vault_id = send_user_vault_id_to_frdr_result[0];
      if (!success_send_vault_id) {
        event.reply('notify-send-entity-id-to-frdr-error', send_user_vault_id_to_frdr_result[1]);
      }
    }
    else if (!success_get_vault_id_from_frdr) {
      event.reply('notify-get-entity-id-from-frdr-error', get_user_vault_id_from_frdr_result[1]);
    }
  }
});