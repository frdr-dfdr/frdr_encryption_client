const flatpickr = require('flatpickr');
const {ipcRenderer} = require('electron');

var expiryDate = null;
var defaultDate = new Date().fp_incr(14);
var defaultDateStr = defaultDate.toISOString().substring(0, 10);
document.getElementById("expiry_date").value = defaultDateStr;
expiryDate = defaultDateStr;
const picker = flatpickr('#expiry_date', {
  minDate: new Date().fp_incr(7),
  maxDate: new Date().fp_incr(30),
  defaultDate: defaultDate,
  allowInput: true,
  onChange: function(selectedDates, dateStr, instance) {
    expiryDate = dateStr;
  }
});

function grantAccess() {
  var dataset = document.getElementById("dataset").value;
  var requester = document.getElementById("requester").value;
  var result;
  var dialogOptions = {
    type: "question",
    buttons: [$.i18n("app-depositor-grant-access-confirm-btn1"), $.i18n("app-depositor-grant-access-confirm-btn2")],
    defaultId: 1,
    title: "Confirmation",
    message: $.i18n("app-depositor-grant-access-confirm")
  }
  ipcRenderer.send("get-entity-name", requester, dataset, expiryDate, dialogOptions);
}

document.getElementById("grant_access").addEventListener("click", grantAccess);

ipcRenderer.on('notify-get-entity-name-error', function (event, result) {
  alert($.i18n('app-depositor-grant-access-find-user-error', result), "");
});

ipcRenderer.on('notify-grant-access-done', function (event) {
  alert($.i18n('app-depositor-grant-access-done'), "");
});

ipcRenderer.on('notify-grant-access-error', function (event, errMessage) {
  alert($.i18n('app-depositor-grant-access-error', errMessage), "");
});