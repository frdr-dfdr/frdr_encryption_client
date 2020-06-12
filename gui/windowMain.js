const notifier = require('node-notifier');
const remote = require('electron').remote;
const tt = require('electron-tooltip');
let client = remote.getGlobal('client');
tt({position: 'right'})

window.onload = myMain;

function myMain() {
  document.getElementById("menu").onclick = selectMode;
}

function selectMode(e) {
  var encryptExtraBlock = document.getElementById("div-encrypt-extra");
  var decryptExtraBlock = document.getElementById("div-decrypt-extra");
  var grantAccessExtraBlock = document.getElementById("div-grant-access-extra");
  if (e.target.id == "button-encrypt") {
    encryptExtraBlock.style.display = "block";
    decryptExtraBlock.style.display = "none";
    grantAccessExtraBlock.style.display = "none";
  }
  else if (e.target.id == "button-decrypt") {
    decryptExtraBlock.style.display = "block";
    encryptExtraBlock.style.display = "none";
    grantAccessExtraBlock.style.display = "none";
  }
  else if (e.target.id == "button-grant-access") {
    decryptExtraBlock.style.display = "none";
    encryptExtraBlock.style.display = "none";
    grantAccessExtraBlock.style.display = "block";
  }
}

var buttonClicked = document.getElementById("button-encrypt");
function highlightButton(element) {
  if (buttonClicked != null) {
    buttonClicked.style.background = "whitesmoke";
    buttonClicked.style.color = "black";
  }
  buttonClicked = element;
  buttonClicked.style.background = "mediumblue";
  buttonClicked.style.color = "white";
}

function encrypt() {
  var hostname = document.getElementById("hostname").value;
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;
  client.invoke("encrypt", username, password, hostname, function(error, res, more) {
    if (res === true){
      notifier.notify({"title" : "FRDR-Crypto", "message" : "Dataset has been encrypted and transfer package has been created on Desktop."});
    } else {
      notifier.notify({"title" : "FRDR-Crypto", "message" : "Error encrypting."});
    }
  });
}

function decrypt() {
  var hostname = document.getElementById("hostname").value;
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;
  var url = document.getElementById("key_url").value;
  client.invoke("decrypt", username, password, hostname, url, function(error, res, more) {
    if (res === true){
      notifier.notify({"title" : "FRDR-Crypto", "message" : "Dataset has been decrypted and placed on Desktop."});
    } else {
      notifier.notify({"title" : "FRDR-Crypto", "message" : "Error decrypting."});
    }
  });
}

function grantAccess() {
  var hostname = document.getElementById("hostname").value;
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;
  var dataset = document.getElementById("dataset").value;
  var requester = document.getElementById("requester").value;
  client.invoke("grant_access", username, password, hostname, dataset, requester, function(error, res, more) {
    if (res === true){
      notifier.notify({"title" : "FRDR-Crypto", "message" : "Access Granted"});
    } else {
      notifier.notify({"title" : "FRDR-Crypto", "message" : "Error access granting."});
    }
  });
}

document.getElementById("GrantAccess").addEventListener("click", grantAccess);

// Send a open directory selector dialog message from a renderer process to main process 
const ipc = require('electron').ipcRenderer
const selectDirBtn = document.getElementById('input_path_dir')
selectDirBtn.addEventListener('click', function (event) {
     ipc.send('open-dir-dialog')
});
//Getting back the information after selecting the dir
ipc.on('selected-dir', function (event, path) {
//print the path selected
document.getElementById('selected-dir').innerHTML = `You selected: ${path}`
});


document.getElementById("encrypt").addEventListener("click", encrypt);

// Send a open file selector dialog message from a renderer process to main process
const selectFileBtn = document.getElementById('input_path_file')
selectFileBtn.addEventListener('click', function (event) {
     ipc.send('open-file-dialog')
});
//Getting back the information after selecting the file
ipc.on('selected-file', function (event, path) {
//print the path selected
document.getElementById('selected-file').innerHTML = `You selected: ${path}`
});

document.getElementById("decrypt").addEventListener("click", decrypt);

