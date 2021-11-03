const flatpickr = require('flatpickr');
const {ipcRenderer} = require('electron');

var expiryDate = null;
var defaultDate = new Date().fp_incr(14);
var defaultDateStr = defaultDate.toISOString().substring(0, 10);
document.getElementById("expiry_date").value = defaultDateStr;
expiryDate = defaultDateStr;
flatpickr('#expiry_date', {
  minDate: new Date().fp_incr(7),
  maxDate: new Date().fp_incr(30),
  defaultDate: defaultDate,
  allowInput: true,
  onChange: function(_selectedDates, dateStr) {
    expiryDate = dateStr;
  }
});

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
  ipcRenderer.send("grant-access", requester, dataset, expiryDate, dialogOptions, dialogOptions2, loginSuccessMsg);
}

ipcRenderer.on('notify-get-entity-name-error', function (_event, result) {
  alert($.i18n('app-depositor-grant-access-find-user-error', result), "");
});

ipcRenderer.on('notify-grant-access-done', function (_event) {
  alert($.i18n('app-depositor-grant-access-done'), "");
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