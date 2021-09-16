const {ipcRenderer} = require("electron");

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
  ipcRenderer.send("login", hostname, hostnamePKI);
}

document.getElementById("globus_submit").addEventListener("click", oidcGlobusLogin);

ipcRenderer.on('notify-login-done', function (event) {
  ipcRenderer.send("authenticated");
});

ipcRenderer.on('notify-login-error', function (event, errMessage) {
  alert(`Error logging in with Globus OAuth. \n${errMessage}`, "")
});