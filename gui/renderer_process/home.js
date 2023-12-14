const {ipcRenderer} = require("electron");

ipcRenderer.on('notify-send-entity-id-to-frdr-error', function (_event, errMessage) {
  alert($.i18n('app-send-entity-id-to-frdr-error', errMessage), "");
});


ipcRenderer.on('notify-get-entity-id-from-frdr-error', function (_event, errMessage) {
  alert($.i18n('app-get-entity-id-from-frdr-error', errMessage), "");
});