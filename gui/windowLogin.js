const notifier = require('node-notifier');
const remote = require('electron').remote;
const tt = require('electron-tooltip');
let client = remote.getGlobal('client');
tt({position: 'right'})

function login() {
  var hostname = document.getElementById("hostname").value;
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;
  client.invoke("get_token", username, password, hostname, function(error, res, more) {
    if (res){
      if (res == "Token obtained.") {
        var window = remote.getCurrentWindow();
        window.close();
      }
      notifier.notify({"title" : "FRDR-Crypto", "message" : res});
    } else {
      setTimeout(notifier.notify({"title" : "FRDR-Crypto", "message" : "No response from server. Is it running and configured properly?"}), 1000)
    }
  });
}

document.getElementById("login").addEventListener("click", login);