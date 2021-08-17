const notifier = require('node-notifier');
const remote = require('electron').remote;
const {dialog} = require('electron').remote;
const {clipboard} = require('electron').remote; 
let client = remote.getGlobal('client');

function generateAccessRequest() {
  client.invoke("get_entity_id", function(error, res, more) {
    var success = res[0];
    var result = res[1];
    if (success) {
      var options = {
        type: 'question',
        buttons: [$.i18n("app-requester-request-access-confirm-btn")],
        defaultId: 0,
        title: 'Question',
        message: $.i18n("app-requester-request-access-confirm-msg"),
        detail: `${result}`,
      };
      const response = dialog.showMessageBoxSync(options);
      if (response == 0) {
        clipboard.writeText(result);
        var options2 = {
          type: "info",
          buttons: [$.i18n("app-requester-request-access-ok-btn")],
          title: "Important Information",
          message: $.i18n('app-requester-request-access-done-msg')
        }
        dialog.showMessageBoxSync(options2);
      }
    }
    else {
      notifier.notify({"title" : $.i18n('app-name'), "message" : $.i18n("app-requester-request-access-error", result)});
    }
  });  
}

document.getElementById("request-access").addEventListener("click", generateAccessRequest);

