const {ipcRenderer} = require('electron');

let input_path = null;
let output_path = null;

// Send a open directory selector dialog message from a renderer process to main process 
$('#input_path_dir').on("click", function(){
  ipcRenderer.send('encrypt-open-input-dir-dialog');
});

//Getting back the information after selecting the dir
ipcRenderer.on('encrypt-selected-input-dir', function (_event, path) {
  //print the path selected
  input_path = path;
  document.getElementById('selected-input-dir').innerHTML = $.i18n('app-depositor-encrypt-selected', path);
});

// Send a open directory selector dialog message from a renderer process to main process 
$('#output_path_dir').on("click", function(){
  ipcRenderer.send('encrypt-open-output-dir-dialog')
});

//Getting back the information after selecting the dir
ipcRenderer.on('encrypt-selected-output-dir', function (_event, path) {
  //print the path selected
  output_path = path;
  document.getElementById('selected-output-dir').innerHTML = $.i18n('app-depositor-encrypt-selected', path);
});

ipcRenderer.on('notify-encrypt-done', function (_event, result) {
  alert($.i18n('app-depositor-encrypt-done', result), "");
});

ipcRenderer.on('notify-encrypt-error', function (_event, result) {
  alert($.i18n('app-depositor-encrypt-error', result), "");
});

$('#encrypt').on("click", function(){
  if (input_path == null){
      alert($.i18n('app-depositor-encrypt-input-missing'));
  }
  else if (output_path == null) {
    alert($.i18n('app-depositor-encrypt-output-missing'));
  }
  else {
    ipcRenderer.send("encrypt", input_path[0], output_path[0]);
  }
});

$('#encrypt-cancel').on("click", function(){
    ipcRenderer.send("encrypt-cancel");
});