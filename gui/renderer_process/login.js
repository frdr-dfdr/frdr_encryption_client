const {ipcRenderer} = require("electron");
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

let vault_authenticated = false;
let frdr_api_authenticated = false;

try {
    let fileContents = fs.readFileSync(path.join(__dirname, '../../config/config.yml'), 'utf8');
    let config = yaml.load(fileContents);
    document.getElementById('hostname').value = config['VAULT_HOSTNAME'];
    document.getElementById('api_base_url').value = config['FRDR_API_BASE_URL'];
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

function APIGlobusLogin() {
  var baseUrl = document.getElementById("api_base_url").value;
  ipcRenderer.send('login-frdr-api-globus', baseUrl);
}

document.getElementById("api_globus_submit").addEventListener("click", APIGlobusLogin);

ipcRenderer.on('notify-login-oidc-done', function (event) {
  vault_authenticated = true;
  if (vault_authenticated && frdr_api_authenticated) {
    ipcRenderer.send("authenticated");
  }
  else {
    alert(`You have successfully logged into Hashicorp Vault. Please click the second login button to use FRDR REST API.`, "")
  }
});

ipcRenderer.on('notify-login-oidc-error', function (event, errMessage) {
  alert(`Error logging in with Globus OAuth. \n${errMessage}`, "")
});

ipcRenderer.on('notify-get-auth-url-error', function (event, errMessage) {
  alert(`Error getting oauth url to log into Vault. \n${errMessage}`, "")
});

ipcRenderer.on('notify-login-frdr-api-done', function (event) {
  frdr_api_authenticated = true;
  if (vault_authenticated && frdr_api_authenticated) {
    ipcRenderer.send("authenticated");
  }
  else {
    alert(`You have successfully logged in to use FRDR REST API. Please click the first login button to log into Hashicorp Vault.`, "")
  }
});

ipcRenderer.on('notify-login-frdr-api-error', function (event, errMessage) {
  alert(`Error logging in with Globus OAuth for FRDR API Usage.  \n${errMessage}`, "")
});