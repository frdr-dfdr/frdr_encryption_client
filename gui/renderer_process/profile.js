const {ipcRenderer} = require('electron');

ipcRenderer.send("get-entity-id");

ipcRenderer.on('notify-get-entity-id-done', function (event, result) {
  document.getElementById("vault_user_id").innerHTML = result;
  ipcRenderer.send("get-entity-name", result);
});

ipcRenderer.on('notify-get-entity-id-error', function (event, errMessage) {
  alert($.i18n('app-get-entity-id-error', errMessage), "");
});

ipcRenderer.on('notify-get-entity-name-done', function (event, result) {
  document.getElementById("vault_email").innerHTML = result;
});

ipcRenderer.on('notify-get-entity-name-error', function (event, errMessage) {
  alert($.i18n('app-get-entity-name-error', errMessage), "");
});