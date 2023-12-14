const {ipcRenderer} = require("electron");
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

var timeout = null;

try {
  var configPath = "";
  if (process.env.NODE_ENV == "development") {
    configPath = path.join(__dirname, '..', '..','config', 'config.yml');
  }
  else {
    var configPath = path.join(__dirname, '..', 'app_gui','config', 'config.yml');
  }
  let fileContents = fs.readFileSync(configPath, 'utf8');
  let config = yaml.load(fileContents);
  timeout = config["VAULT_LOGIN_TIMEOUT"];
} catch (e) {
  // log error, but the login workflow still works
  console.log(e);
}

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
})

function vaultOIDCGlobusLogin() {

  var countdownNum = timeout;
  incTimer();

  function incTimer(){
    setTimeout (function(){
      if(countdownNum != 0){
        countdownNum--;
        document.getElementById("globus_submit").disabled = true;
        document.getElementById('globus_submit').innerHTML = $.i18n('app-login-vault-btn') + ' (' + countdownNum + 's)';
        incTimer();
      } else {
        document.getElementById("globus_submit").disabled = false;
        document.getElementById('globus_submit').innerHTML = $.i18n('app-login-vault-btn');
      }
    },1000);
  }

  var loginSuccessMsg = $.i18n("app-login-vault-success-message");
  ipcRenderer.send("login-vault-oidc-globus", loginSuccessMsg);
}

ipcRenderer.on('notify-login-oidc-done', function (_event) {
  ipcRenderer.send("verify-local-user-keys");
});

ipcRenderer.on('notify-login-oidc-error', function (_event, errMessage) {
  alert($.i18n('app-login-vault-error', errMessage), "");
});

ipcRenderer.on('notify-verify-local-user-keys-error', function (_event, errMessage) {
  var dialogOptions = {
    type: "warning",
    buttons: [$.i18n("app-cancel-btn")],
    title: "Error",
    message: errMessage
  };
  ipcRenderer.send("verification-failed", dialogOptions);
});

ipcRenderer.on('notify-verify-local-user-keys-done', function (_event) {
  ipcRenderer.send("authenticated");
  ipcRenderer.send("sync-entity-id");
});