const notifier = require('node-notifier');
const path = require('path');
const remote = require('electron').remote;
const {dialog} = require('electron').remote;
const {shell} = require('electron').remote;
let client = remote.getGlobal('client');
const root = document.documentElement;

let input_path = null;
let output_path = null;

function encrypt() {
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
    pathname: path.join(__dirname, 'depositor-encrypt-in-progress.html'),
    protocol: 'file:',
    slashes: true
  }));
  childWindow.once('ready-to-show', () => {
    childWindow.show()
  });
  client.invoke("encrypt", input_path[0], output_path[0], function(error, res, more) {
    var success = res[0];
    var result = res[1];
    childWindow.close();
    if (success){
      // TODO: add a pop up window for notification
      notifier.notify({"title" : $.i18n('app-name'), "message" : $.i18n('app-depositor-encrypt-done', result)});
      shell.showItemInFolder(result);
    } else {
      // TODO: add a pop up window for notification
      notifier.notify({"title" : $.i18n('app-name'), "message" : $.i18n('app-depositor-encrypt-error', result)});
    }
  });
}

// Send a open directory selector dialog message from a renderer process to main process 
const ipc = require('electron').ipcRenderer
const selectInputDirBtn = document.getElementById('input_path_dir')
selectInputDirBtn.addEventListener('click', function (event) {
  ipc.send('open-input-dir-dialog')
});
//Getting back the information after selecting the dir
ipc.on('selected-input-dir', function (event, path) {
  //print the path selected
  input_path = path;
  document.getElementById('selected-input-dir').innerHTML = $.i18n('app-depositor-encrypt-selected', path);
});

// Send a open directory selector dialog message from a renderer process to main process 
const selectOutputDirBtn = document.getElementById('output_path_dir')
selectOutputDirBtn.addEventListener('click', function (event) {
  ipc.send('open-output-dir-dialog')
});
//Getting back the information after selecting the dir
ipc.on('selected-output-dir', function (event, path) {
  //print the path selected
  output_path = path;
  document.getElementById('selected-output-dir').innerHTML = $.i18n('app-depositor-encrypt-selected', path);
});

document.getElementById("encrypt").addEventListener("click", encrypt);

ipc.on("loaded", (e, data) => {
  colors = data.colors;
  console.log(colors);
  root.style.setProperty("--heading-text-color", colors.general.header_color);
  ipc.send("load-end");
});