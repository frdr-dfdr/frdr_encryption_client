const notifier = require('node-notifier');
const remote = require('electron').remote;
const tt = require('electron-tooltip');
let client = remote.getGlobal('client');
tt({position: 'right'})

function encrypt() {
  var hostname = document.getElementById("hostname").value;
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;
  console.log(hostname);
  client.invoke("encrypt", username, password, hostname, function(error, res, more) {
    if (res === true){
      var window = remote.getCurrentWindow();
      window.close();
      notifier.notify({"title" : "FRDR-Crypto", "message" : "Dataset has been encrypted and transfer package has been created."});
    } else {
      notifier.notify({"title" : "FRDR-Crypto", "message" : "Error encrypting."});
    }
  });
}

const ipc = require('electron').ipcRenderer
const selectDirBtn = document.getElementById('input_path')

selectDirBtn.addEventListener('click', function (event) {
     ipc.send('open-file-dialog')
});

//Getting back the information after selecting the file
ipc.on('selected-file', function (event, path) {
//print the path selected
document.getElementById('selected-file').innerHTML = `You selected: ${path}`
});

document.getElementById("encrypt").addEventListener("click", encrypt);

