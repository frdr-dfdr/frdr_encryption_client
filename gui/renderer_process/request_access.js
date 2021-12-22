const {ipcRenderer, shell} = require('electron');
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

var profileURL = null;

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
  profileURL = config["FRDR_PROFILE_URL"];
} catch (e) {
  // log error, the link to FRDR profile page is not working
  console.log(e);
}

function generateAccessRequest() {
  var dialogOptions = {
    type: 'question',
    buttons: [$.i18n("app-request-access-confirm-btn")],
    defaultId: 0,
    title: 'Question',
    message: $.i18n("app-request-access-confirm-msg"),
  };

  var copiedDoneDialogOptions = {
    type: "info",
    buttons: [$.i18n("app-request-access-ok-btn")],
    title: "Important Information",
    message: $.i18n('app-request-access-done-msg')
  }

  ipcRenderer.send("request-access", dialogOptions, copiedDoneDialogOptions);
}

document.getElementById("request-access").addEventListener("click", generateAccessRequest);

ipcRenderer.on('notify-request-access-error', function (_event, result) {
  alert($.i18n('app-request-access-error', result), "");
});

function openFRDRProfile() {
  shell.openExternal(profileURL);
}

document.getElementById("open-frdr-profile").addEventListener("click", openFRDRProfile);