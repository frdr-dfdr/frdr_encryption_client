const {ipcRenderer} = require("electron");
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

let vault_authenticated = false;

try {
    let fileContents = fs.readFileSync(path.join(__dirname, '../../config/config.yml'), 'utf8');
    let config = yaml.load(fileContents);
    document.getElementById('hostname').value = config['VAULT_HOSTNAME'];
} catch (e) {
  // TODO: log error?
  console.log(e);
}

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
  ipcRenderer.send("login-vault-oidc-globus", hostname, hostnamePKI);
}

document.getElementById("globus_submit").addEventListener("click", oidcGlobusLogin);

ipcRenderer.on('notify-login-oidc-done', function (event) {
  ipcRenderer.send("authenticated");
});

ipcRenderer.on('notify-login-oidc-error', function (event, errMessage) {
  alert(`Error logging in with Globus OAuth. \n${errMessage}`, "")
});