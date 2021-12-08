const {ipcRenderer} = require('electron');

function grantAccess() {
  var dataset = document.getElementById("dataset").value.trim();
  var requester = document.getElementById("requester").value.trim();
  var dialogOptions = {
    type: "question",
    buttons: [$.i18n("app-depositor-grant-access-confirm-btn1"), $.i18n("app-depositor-grant-access-confirm-btn2")],
    defaultId: 1,
    title: "Confirmation",
    message: $.i18n("app-depositor-grant-access-confirm")
  };
  var dialogOptions2 = {
    type: "question",
    buttons: [$.i18n("app-depositor-grant-access-login-api-btn1"), $.i18n("app-depositor-grant-access-login-api-btn2")],
    defaultId: 1,
    title: "Confirmation",
    message: $.i18n("app-depositor-grant-access-login-api")
  };
  var loginSuccessMsg = $.i18n("app-depositor-grant-access-login-success-message");
  ipcRenderer.send("grant-access", requester, dataset, dialogOptions, dialogOptions2, loginSuccessMsg);
}

ipcRenderer.on('notify-get-entity-name-error', function (_event, result) {
  alert($.i18n('app-depositor-grant-access-find-user-error', result), "");
});

ipcRenderer.on('notify-get-dataset-title-error', function (_event, result) {
  alert($.i18n('app-depositor-grant-access-find-dataset-error', result), "");
});

ipcRenderer.on('notify-grant-access-done', function (_event) {
  alert($.i18n('app-depositor-grant-access-done'), "");
  ipcRenderer.send('grant-access-done-show-next-step');
});

ipcRenderer.on('notify-grant-access-error', function (_event, errMessage) {
  alert($.i18n('app-depositor-grant-access-error', errMessage), "");
});

ipcRenderer.on('notify-login-frdr-api-error', function (_event, errMessage) {
  alert(`Error logging in with Globus OAuth for FRDR API Usage.  \n${errMessage}`, "")
});

$('#grant_access').on("click", function(){
  if ($("#dataset").val() == "") {
    alert($.i18n('app-depositor-grant-access-dataset-missing'));
  }
  else if ($("#requester").val() == "") {
    alert($.i18n('app-depositor-grant-access-requester-missing'));
  }
  else {
    grantAccess();
  }
});