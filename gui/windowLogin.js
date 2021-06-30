"use strict";

const notifier = require('node-notifier');
const path = require('path');
const remote = require('electron').remote;
const {dialog} = require('electron').remote;
const {shell} = require('electron').remote;
const {ipcRenderer} = require("electron");
const flatpickr = require('flatpickr');
const {clipboard} = require('electron').remote; 
let client = remote.getGlobal('client');

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
})

function userpassLogin() {
  var hostname = document.getElementById("hostname").value;
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;
  var token = document.getElementById("token").value;
  var options = {
    type: "question",
    buttons: ["Select Output Directory"],
    defaultId: 1,
    title: "Confirmation",
    message: `Please select an output path for the encrypted package.`
  }
  const response = dialog.showMessageBoxSync(options);
  if (response == 0) {
    var output_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
  }
  if (typeof(output_path) == "undefined") {
    return;
  }
  var window = remote.getCurrentWindow();
    var childWindow = new remote.BrowserWindow({ 
      parent: window, 
      modal: true, 
      show: false, 
      width: 300, 
      height: 100, 
      webPreferences: {
        nodeIntegration: true
      }
    });
    childWindow.loadURL(require('url').format({
      pathname: path.join(__dirname, 'indexEncryptInProgress.html'),
      protocol: 'file:',
      slashes: true
    }));
    childWindow.once('ready-to-show', () => {
      childWindow.show()
    });
  client.invoke("login", username, password, token, hostname, output_path[0], function(error, res, more) {
    var success = res[0];
    var result = res[1];
    childWindow.close();
    if (success){
      notifier.notify({"title" : "FRDR Encryption Application", "message" : `Dataset has been encrypted and transfer package has been created on ${result}.`});
      shell.showItemInFolder(result)
    } else {
      notifier.notify({"title" : "FRDR Encryption Application", "message" : `Error encrypting. ${result}`});
    }
  });
}

function oidcGoogleLogin() {
  var hostname = document.getElementById("hostname").value;
  client.invoke("login_oidc_google", hostname, function(error, res, more) {
    var success = res[0];
    var errMessage = res[1];
    if (success) {
      ipcRenderer.send("authenticated")
    }
    else {
      alert({"title" : "FRDR Encryption Application", "message" : `Error reviewing shares. \n${errMessage}`});
      // notifier.notify({"title" : "FRDR Encryption Application", "message" : `Error reviewing shares. \n${errMessage}`});
    }
  });
}

function oidcGlobusLogin() {
  var hostname = document.getElementById("hostname").value;
  var hostnamePKI = document.getElementById("pki-hostname").value;
  client.invoke("login_oidc_globus", hostname, hostnamePKI, function(error, res, more) {
    var success = res[0];
    var errMessage = res[1];
    if (success) {
      ipcRenderer.send("authenticated")
    }
    else {
      alert({"title" : "FRDR Encryption Application", "message" : `Error reviewing shares. \n${errMessage}`});
      // notifier.notify({"title" : "FRDR Encryption Application", "message" : `Error reviewing shares. \n${errMessage}`});
    }
  });
}


document.getElementById("userpass_submit").addEventListener("click", userpassLogin);

document.getElementById("google_submit").addEventListener("click", oidcGoogleLogin);

document.getElementById("globus_submit").addEventListener("click", oidcGlobusLogin);




