const notifier = require('node-notifier');
const path = require('path');
const remote = require('electron').remote;
const {dialog} = require('electron').remote;
let client = remote.getGlobal('client');

let input_path = null;
let output_path = null;

function decrypt() {
  var url = document.getElementById("key_url").value;
  var dataset = url.split("/").reverse()[1];
  var options = {
    type: "question",
    buttons: [$.i18n("app-requester-decrypt-confirm-btn1"), $.i18n("app-requester-decrypt-confirm-btn2")],
    defaultId: 1,
    title: "Confirmation",
    message: $.i18n("app-requester-decrypt-confirm", dataset)
  }
  const response = dialog.showMessageBoxSync(options);
  if (response == 0) {
    var window = remote.getCurrentWindow();
    var childWindow = new remote.BrowserWindow({ 
      parent: window, 
      modal: true, 
      show: false, 
      width: 400, 
      height: 200,
      webPreferences: {
        nodeIntegration: true
      } 
    });
    childWindow.loadURL(require('url').format({
      pathname: path.join(__dirname, 'requester-decrypt-in-progress.html'),
      protocol: 'file:',
      slashes: true
    }));
    childWindow.once('ready-to-show', () => {
      childWindow.show()
    });
    client.invoke("decrypt", input_path[0], output_path[0], url, function(error, res, more) {
      childWindow.close();
      var success = res[0];
      var errMessage = res[1];
      if (success){
        notifier.notify({"title" : $.i18n('app-name'), "message" : $.i18n("app-requester-decrypt-done")});
      } else {
        notifier.notify({"title" : $.i18n('app-name'), "message" : $.i18n("app-requester-decrypt-error", errMessage)});
      }
    });
  }
}

// Send a open directory selector dialog message from a renderer process to main process 
const ipc = require('electron').ipcRenderer

const selectOutputDirBtn = document.getElementById('output_path_dir')
selectOutputDirBtn.addEventListener('click', function (event) {
  ipc.send('open-output-dir-dialog')
});
//Getting back the information after selecting the dir
ipc.on('selected-output-dir', function (event, path) {
  output_path = path;
  //print the path selected
  document.getElementById('selected-output-dir').innerHTML = $.i18n('app-requester-decrypt-selected', path);
});

// Send a open file selector dialog message from a renderer process to main process
const selectFileBtn = document.getElementById('input_path_file')
selectFileBtn.addEventListener('click', function (event) {
     ipc.send('open-file-dialog')
});
//Getting back the information after selecting the file
ipc.on('selected-file', function (event, path) {
  input_path = path;
  //print the path selected
  document.getElementById('selected-file').innerHTML = $.i18n('app-requester-decrypt-selected', path);
});

document.getElementById("decrypt").addEventListener("click", decrypt);
