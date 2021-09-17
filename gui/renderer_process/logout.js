const notifier = require('node-notifier');
const remote = require('electron').remote;
const {dialog} = require('electron').remote;
let client = remote.getGlobal('client');
const ipc = require('electron').ipcRenderer;

// Allow the user to logout
document.getElementById("logout").addEventListener("click", logout);

function logout() {
  var url = "https://auth.globus.org/v2/web/logout";
  const win = new remote.BrowserWindow({width: 800, height: 600});
  win.loadURL(url);
  client.invoke("logout", function(error, res, more) {
    var success = res[0];
    var result = res[1];
    console.log(success);
    if (success){
      // notifier.notify({"title" : $.i18n('app-name'), "message" : $.i18n('app-logout')});
      // var options = {
      //   type: 'info',
      //   buttons: ['Close'],
      //   defaultId: 0,
      //   title: $.i18n('app-name'),
      //   message: $.i18n('app-logout'),
      // };
      // const response = dialog.showMessageBoxSync(options);
      ipc.send("unauthenticated");
    } else {
      notifier.notify({"title" : "FRDR Encryption Application", "message" : `Error logging out. ${result}`});
    }
  });
  
}
