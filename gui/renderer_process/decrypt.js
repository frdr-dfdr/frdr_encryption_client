const {ipcRenderer} = require('electron');

let input_path = null;
let output_path = null;

// Send a open file selector dialog message from a renderer process to main process
const selectFileBtn = document.getElementById('input_path_file')
selectFileBtn.addEventListener('click', function (_event) {
     ipcRenderer.send('decrypt-open-file-dialog')
});
//Getting back the information after selecting the file
ipcRenderer.on('decrypt-selected-file', function (_event, path) {
  input_path = path;
  //print the path selected
  document.getElementById('selected-file').innerHTML = $.i18n('app-decrypt-selected', path);
});

// Send a open directory selector dialog message from a renderer process to main process 
const selectOutputDirBtn = document.getElementById('output_path_dir')
selectOutputDirBtn.addEventListener('click', function (_event) {
  ipcRenderer.send('decrypt-open-output-dir-dialog')
});
//Getting back the information after selecting the dir
ipcRenderer.on('decrypt-selected-output-dir', function (_event, path) {
  output_path = path;
  //print the path selected
  document.getElementById('selected-output-dir').innerHTML = $.i18n('app-decrypt-selected', path);
});

function decrypt() {
  var url = document.getElementById("key_url").value.trim();
  var dataset = url.split("/").reverse()[1];
  var options = {
    type: "question",
    buttons: [$.i18n("app-decrypt-confirm-btn1"), $.i18n("app-decrypt-confirm-btn2")],
    defaultId: 1,
    title: "Confirmation",
    message: $.i18n("app-decrypt-confirm")
  }
  ipcRenderer.send("decrypt", dataset, options, input_path[0], output_path[0], url);
}

ipcRenderer.on('notify-decrypt-done', function (_event) {
  alert($.i18n('app-decrypt-done'), "");
});

ipcRenderer.on('notify-decrypt-error', function (_event, errMessage) {
  alert($.i18n('app-decrypt-error', errMessage), "");
});

$('#decrypt').on("click", function(){
  if ($("#key_url").val() == "") {
    alert($.i18n('app-decrypt-url-missing'));
  }
  else if (input_path == null){
    alert($.i18n('app-decrypt-input-missing'));
  }
  else if (output_path == null) {
    alert($.i18n('app-decrypt-output-missing'));
  }
  else {
    decrypt();
  }
});