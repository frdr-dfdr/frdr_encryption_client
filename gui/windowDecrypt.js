const notifier = require('node-notifier');
const remote = require('electron').remote;
const tt = require('electron-tooltip');
let client = remote.getGlobal('client');
tt({position: 'right'})

function decrypt() {
  var hostname = document.getElementById("hostname").value;
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;
  var url = document.getElementById("key_url").value;
  console.log(hostname);
  client.invoke("decrypt", username, password, hostname, url, function(error, res, more) {
    if (res === true){
      var window = remote.getCurrentWindow();
      window.close();
      notifier.notify({"title" : "FRDR-Crypto", "message" : "Dataset has been decrypted for access."});
    } else {
      notifier.notify({"title" : "FRDR-Crypto", "message" : "Error decrypting."});
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

document.getElementById("decrypt").addEventListener("click", decrypt);

