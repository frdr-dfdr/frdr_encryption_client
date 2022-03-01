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
  document.getElementById('hostname').value = config['VAULT_HOSTNAME'];
  timeout = config["VAULT_LOGIN_TIMEOUT"];
} catch (e) {
  // log error, but the login workflow still works
  console.log(e);
}

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
})

function oidcGlobusLogin() {

  var countdownNum = timeout;
  incTimer();

  function incTimer(){
    setTimeout (function(){
      if(countdownNum != 0){
        countdownNum--;
        document.getElementById("globus_submit").disabled = true;
        document.getElementById('globus_submit').innerHTML = $.i18n('app-login-btn') + ' (' + countdownNum + 's)';
        incTimer();
      } else {
        document.getElementById("globus_submit").disabled = false;
        document.getElementById('globus_submit').innerHTML = $.i18n('app-login-btn');
      }
    },1000);
  }

  var hostname = document.getElementById("hostname").value;
  if (document.getElementById("pki-hostname") != null) {
    var hostnamePKI = document.getElementById("pki-hostname").value;
  }
  else {
    var hostnamePKI = hostname;
  }
  var loginSuccessMsg = $.i18n("app-login-success-message");
  ipcRenderer.send("login-vault-oidc-globus", hostname, hostnamePKI, loginSuccessMsg);
}

ipcRenderer.on('notify-login-oidc-done', function (_event) {
  ipcRenderer.send("verify-local-user-keys");
});

ipcRenderer.on('notify-login-oidc-error', function (_event, errMessage) {
  alert($.i18n('app-login-error', errMessage), "");
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
});