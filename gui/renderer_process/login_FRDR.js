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
  timeout = config["FRDR_API_LOGIN_TIMEOUT"];
} catch (e) {
  // log error, but the login workflow still works
  console.log(e);
}

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
})

function FRDRGlobusLogin() {

  var countdownNum = timeout;
  incTimer();

  function incTimer(){
    setTimeout (function(){
      if(countdownNum != 0){
        countdownNum--;
        document.getElementById("globus_submit").disabled = true;
        document.getElementById('globus_submit').innerHTML = $.i18n('app-login-frdr-btn') + ' (' + countdownNum + 's)';
        incTimer();
      } else {
        document.getElementById("globus_submit").disabled = false;
        document.getElementById('globus_submit').innerHTML = $.i18n('app-login-frdr-btn');
      }
    },1000);
  }

  var loginSuccessMsg = $.i18n("app-login-frdr-success-message");
  ipcRenderer.send("login-frdr-api-globus", loginSuccessMsg);
}

ipcRenderer.on('notify-login-frdr-done', function (_event) {
  ipcRenderer.send("frdr-authenticated");
});

ipcRenderer.on('notify-login-frdr-error', function (_event, errMessage) {
  alert($.i18n('app-login-frdr-error', errMessage), "");
});