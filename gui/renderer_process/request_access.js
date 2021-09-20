const {ipcRenderer} = require('electron');

function generateAccessRequest() {
  var dialogOptions = {
    type: 'question',
    buttons: [$.i18n("app-requester-request-access-confirm-btn")],
    defaultId: 0,
    title: 'Question',
    message: $.i18n("app-requester-request-access-confirm-msg"),
  };

  var copiedDoneDialogOptions = {
    type: "info",
    buttons: [$.i18n("app-requester-request-access-ok-btn")],
    title: "Important Information",
    message: $.i18n('app-requester-request-access-done-msg')
  }

  ipcRenderer.send("request-access", dialogOptions, copiedDoneDialogOptions);
}

document.getElementById("request-access").addEventListener("click", generateAccessRequest);

ipcRenderer.on('notify-request-access-error', function (event, result) {
  alert($.i18n('app-requester-request-access-error', result), "");
});