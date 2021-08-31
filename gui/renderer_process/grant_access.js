const notifier = require('node-notifier');
const remote = require('electron').remote;
const {dialog} = require('electron').remote;
const flatpickr = require('flatpickr');
let client = remote.getGlobal('client');

var expiryDate = null;
var defaultDate = new Date().fp_incr(14);
var defaultDateStr = defaultDate.toISOString().substring(0, 10);
document.getElementById("expiry_date").value = defaultDateStr;
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

  client.invoke("get_entity_name", requester, function(error, res, more) {
    var success = res[0];
    var result = res[1];
    if (success && result != null) {
      var options = {
        type: "question",
        buttons: [$.i18n("app-depositor-grant-access-confirm-btn1"), $.i18n("app-depositor-grant-access-confirm-btn2")],
        defaultId: 1,
        title: "Confirmation",
        message: $.i18n("app-depositor-grant-access-confirm", result, dataset)
      }
      const response = dialog.showMessageBoxSync(options);
      if (response == 0){
        client.invoke("grant_access", dataset, requester, expiryDate, function(error, res, more) {
          var grant_access_success = res[0];
          var grant_access_result = res[1];
          if (grant_access_success){
            // TODO: add a pop up window for notification
            notifier.notify({"title" : $.i18n('app-name'), "message" : $.i18n('app-depositor-grant-access-done')});
          } else {
            // TODO: add a pop up window for notification
            notifier.notify({"title" : $.i18n('app-name'), "message" : $.i18n('app-depositor-grant-access-error', grant_access_result)});
          }
        });
      }
    }
    else {
      notifier.notify({"title" : $.i18n('app-name'), "message" : $.i18n('app-depositor-grant-access-find-user-error', result)});
    }
  });
}

document.getElementById("grant_access").addEventListener("click", grantAccess);
