const notifier = require('node-notifier');
const path = require('path');
const remote = require('electron').remote;
const {dialog} = require('electron').remote;
const {shell} = require('electron').remote;
const {ipcRenderer} = require("electron");
let client = remote.getGlobal('client');
const ipc = require('electron').ipcRenderer;
const root = document.documentElement;

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
})

function oidcGlobusLogin() {
  var hostname = document.getElementById("hostname").value;
  if (document.getElementById("pki-hostname") != null) {
    var hostnamePKI = document.getElementById("pki-hostname").value;
  }
  else {
    var hostnamePKI = hostname
  }

  client.invoke("login_oidc_globus", hostname, hostnamePKI, function(error, res, more) {
    var success = res[0];
    var errMessage = res[1];
    if (success) {
      ipcRenderer.send("authenticated")
    }
    else {
      alert({"title" : "FRDR Encryption Application", "message" : `Error logging in with Globus OAuth. \n${errMessage}`});
      // notifier.notify({"title" : "FRDR Encryption Application", "message" : `Error logging in with Globus OAuth. \n${errMessage}`});
    }
  });
}

document.getElementById("globus_submit").addEventListener("click", oidcGlobusLogin);



ipc.on("loaded", (e, data) => {
  colors = data.colors;
  console.log(colors);
  root.style.setProperty("--heading-text-color", colors.general.header_color);
  ipc.send("load-end");
});
