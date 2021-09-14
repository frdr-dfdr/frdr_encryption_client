const notifier = require('node-notifier');
const path = require('path');
const remote = require('electron').remote;
const {dialog} = require('electron').remote;
const {shell} = require('electron').remote;
const {ipcRenderer} = require("electron");
let client = remote.getGlobal('client');
const ipc = require('electron').ipcRenderer;
const root = document.documentElement;
const fs = require('fs');
const yaml = require('js-yaml');

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

  client.invoke("login_oidc_globus", hostname, hostnamePKI, function(error, res, more) {
    var success = res[0];
    var errMessage = res[1];
    success = false;
    if (success) {
      vault_authenticated = true;
      if (vault_authenticated && frdr_api_authenticated) {
        ipcRenderer.send("authenticated");
      }
    }
    else {
      // FIXME: alert not working
      alert({"title" : "FRDR Encryption Application", "message" : `Error logging in with Globus OAuth. \n${errMessage}`});
      // notifier.notify({"title" : "FRDR Encryption Application", "message" : `Error logging in with Globus OAuth. \n${errMessage}`});
    }
  });
}

document.getElementById("globus_submit").addEventListener("click", oidcGlobusLogin);

function APIGlobusLogin() {
  var baseUrl = document.getElementById("api_base_url").value;

  client.invoke("login_frdr_api_globus", baseUrl, function(error, res, more) {
    var success = res[0];
    var errMessage = res[1];
    if (success) {
      frdr_api_authenticated = true;
      if (vault_authenticated && frdr_api_authenticated) {
        ipcRenderer.send("authenticated");
      }
    }
    else {
      alert({"title" : "FRDR Encryption Application", "message" : `Error logging in with Globus OAuth for FRDR API Usage. \n${errMessage}`});
      // notifier.notify({"title" : "FRDR Encryption Application", "message" : `Error logging in with Globus OAuth. \n${errMessage}`});
    }
  });
}

document.getElementById("api_globus_submit").addEventListener("click", APIGlobusLogin);

