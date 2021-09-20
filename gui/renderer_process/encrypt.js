const {ipcRenderer} = require('electron');

let input_path = null;
let output_path = null;

// Send a open directory selector dialog message from a renderer process to main process 
const selectInputDirBtn = document.getElementById('input_path_dir')
selectInputDirBtn.addEventListener('click', function (event) {
  ipcRenderer.send('encrypt-open-input-dir-dialog')
});
//Getting back the information after selecting the dir
ipcRenderer.on('encrypt-selected-input-dir', function (event, path) {
  //print the path selected
  input_path = path;
  document.getElementById('selected-input-dir').innerHTML = $.i18n('app-depositor-encrypt-selected', path);
});

// Send a open directory selector dialog message from a renderer process to main process 
const selectOutputDirBtn = document.getElementById('output_path_dir')
selectOutputDirBtn.addEventListener('click', function (event) {
  ipcRenderer.send('encrypt-open-output-dir-dialog')
});
//Getting back the information after selecting the dir
ipcRenderer.on('encrypt-selected-output-dir', function (event, path) {
  //print the path selected
  output_path = path;
  document.getElementById('selected-output-dir').innerHTML = $.i18n('app-depositor-encrypt-selected', path);
});

function encrypt() {
  ipcRenderer.send("encrypt", input_path[0], output_path[0]);
}
document.getElementById("encrypt").addEventListener("click", encrypt);

ipcRenderer.on('notify-encrypt-done', function (event, result) {
  alert($.i18n('app-depositor-encrypt-done', result), "");
});

ipcRenderer.on('notify-encrypt-error', function (event, result) {
  alert($.i18n('app-depositor-encrypt-error', result), "");
});
