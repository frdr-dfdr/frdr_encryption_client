const notifier = require('node-notifier');
const remote = require('electron').remote;
const tt = require('electron-tooltip');
let client = remote.getGlobal('client');
tt({position: 'right'})

function grantAccess() {
  var hostname = document.getElementById("hostname").value;
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;
  var dataset = document.getElementById("dataset").value;
  var requester = document.getElementById("requester").value;
  client.invoke("grant_access", username, password, hostname, dataset, requester, function(error, res, more) {
    if (res === true){
      var window = remote.getCurrentWindow();
      window.close();
      notifier.notify({"title" : "FRDR-Crypto", "message" : "Access Granted"});
    } else {
      notifier.notify({"title" : "FRDR-Crypto", "message" : "Error granting access."});
    }
  });
}

document.getElementById("GrantAccess").addEventListener("click", grantAccess);

