"use strict";

const notifier = require('node-notifier');
const path = require('path');
const remote = require('electron').remote;
const {dialog} = require('electron').remote;
const {shell} = require('electron').remote;
const flatpickr = require('flatpickr');
let client = remote.getGlobal('client');

var expiryDate = null;
var defaultDate = new Date().fp_incr(14);
var defaultDateStr = defaultDate.toISOString().substring(0, 10);
document.getElementById("expiry_date").value = defaultDateStr;
const picker = flatpickr('#expiry_date', {
  minDate: "today",
  defaultDate: defaultDate,
  onChange: function(selectedDates, dateStr, instance) {
    expiryDate = dateStr;
  }
});


window.onload = myMain;

function myMain() {
  document.getElementById("menu").onclick = selectMode;
}

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
})

function selectMode(e) {
  var encryptExtraBlock = document.getElementById("div-encrypt-extra");
  var decryptExtraBlock = document.getElementById("div-decrypt-extra");
  var grantAccessExtraBlock = document.getElementById("div-grant-access-extra");
  var reviewSharesExtraBlock = document.getElementById("div-review-shares-extra");
  if (e.target.id == "button-encrypt") {
    encryptExtraBlock.style.display = "block";
    decryptExtraBlock.style.display = "none";
    grantAccessExtraBlock.style.display = "none";
    reviewSharesExtraBlock.style.display = "none";
  }
  else if (e.target.id == "button-decrypt") {
    decryptExtraBlock.style.display = "block";
    encryptExtraBlock.style.display = "none";
    grantAccessExtraBlock.style.display = "none";
    reviewSharesExtraBlock.style.display = "none";
  }
  else if (e.target.id == "button-grant-access") {
    decryptExtraBlock.style.display = "none";
    encryptExtraBlock.style.display = "none";
    grantAccessExtraBlock.style.display = "block";
    reviewSharesExtraBlock.style.display = "none";
  }
  else if (e.target.id == "button-review-shares") {
    decryptExtraBlock.style.display = "none";
    encryptExtraBlock.style.display = "none";
    grantAccessExtraBlock.style.display = "none";
    reviewSharesExtraBlock.style.display = "block";
  }
}

var buttonClicked = document.getElementById("button-encrypt");
function highlightButton(element) {
  if (buttonClicked != null) {
    buttonClicked.classList.remove("active")
  }
  buttonClicked = element;
  buttonClicked.classList.add("active")
}

function clearFields() {
  var inputs = document.getElementsByTagName("input");
  for(var i = 0; i < inputs.length; i++) {
    if (inputs[i].id == "expiry_date") {
      inputs[i].value = defaultDateStr;
      continue;
    }
    inputs[i].value = "";
  }
  unsetInputPath();
}

function unsetInputPath() {
  client.invoke("unset_input_path", function(error, res, more){});
  document.getElementById("selected-dir").innerHTML = "No selection";
  document.getElementById("selected-file").innerHTML = "No selection";
}
 
function encrypt() {
  var hostname = document.getElementById("hostname").value;
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;
  var options = {
    type: "question",
    buttons: ["Select Output Directory"],
    defaultId: 1,
    title: "Confirmation",
    message: `Please select an output path for the encrypted package.`
  }
  const response = dialog.showMessageBoxSync(options);
  if (response == 0) {
    var output_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
  }
  if (typeof(output_path) == "undefined") {
    return;
  }
  var window = remote.getCurrentWindow();
    var childWindow = new remote.BrowserWindow({ 
      parent: window, 
      modal: true, 
      show: false, 
      width: 200, 
      height: 100, 
      webPreferences: {
        nodeIntegration: true
      }
    });
    childWindow.loadURL(require('url').format({
      pathname: path.join(__dirname, 'indexEncryptInProgress.html'),
      protocol: 'file:',
      slashes: true
    }));
    childWindow.once('ready-to-show', () => {
      childWindow.show()
    });
  client.invoke("encrypt", username, password, hostname, output_path[0], function(error, res, more) {
    var success = res[0];
    var result = res[1];
    childWindow.close();
    if (success){
      notifier.notify({"title" : "FRDR-Crypto", "message" : `Dataset has been encrypted and transfer package has been created on ${result}.`});
      shell.showItemInFolder(result)
    } else {
      notifier.notify({"title" : "FRDR-Crypto", "message" : `Error encrypting. ${result}`});
    }
  });
}

function decrypt() {
  var hostname = document.getElementById("hostname").value;
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;
  var url = document.getElementById("key_url").value;
  var dataset = url.split("/").pop();
  var options = {
    type: "question",
    buttons: ["Yes", "Cancel"],
    defaultId: 1,
    title: "Confirmation",
    message: `You are trying to decrypt the dataset ${dataset}. \n\nYou should only do this if you're on a trusted computer, as the risk of this data being accessed by another party may be very high.\n\nDo you want to continue?`
  }
  const response = dialog.showMessageBoxSync(options);
  if (response == 0) {
    var selectOutputMessageOptions = {
      type: "question",
      buttons: ["Select Output Directory"],
      defaultId: 1,
      title: "Confirmation",
      message: `Please select an output path for the decrypted package.`
    }
    const selectOutputMessageResponse = dialog.showMessageBoxSync(selectOutputMessageOptions);
    if (selectOutputMessageResponse == 0) {
      var output_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
    }
    if (typeof(output_path) == "undefined") {
      return;
    }
    var window = remote.getCurrentWindow();
    var childWindow = new remote.BrowserWindow({ 
      parent: window, 
      modal: true, 
      show: false, 
      width: 200, 
      height: 100,
      webPreferences: {
        nodeIntegration: true
      } 
    });
    childWindow.loadURL(require('url').format({
      pathname: path.join(__dirname, 'indexDecryptInProgress.html'),
      protocol: 'file:',
      slashes: true
    }));
    childWindow.once('ready-to-show', () => {
      childWindow.show()
    });
    client.invoke("decrypt", username, password, hostname, url, output_path[0], function(error, res, more) {
      childWindow.close();
      var success = res[0];
      var errMessage = res[1];
      if (success){
        notifier.notify({"title" : "FRDR-Crypto", "message" : "Dataset has been decrypted for access."});
      } else {
        notifier.notify({"title" : "FRDR-Crypto", "message" : `Error decrypting. ${errMessage}`});
      }
    });
  }
}

function grantAccess() {
  var hostname = document.getElementById("hostname").value;
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;
  var dataset = document.getElementById("dataset").value;
  var requester = document.getElementById("requester").value;

  client.invoke("get_entity_name", username, password, hostname, requester, function(error, res, more) {
    var success = res[0];
    var result = res[1];
    if (success) {
      var options = {
        type: "question",
        buttons: ["Yes", "Cancel"],
        defaultId: 1,
        title: "Confirmation",
        message: `You are trying to grant requester ${result} access to dataset ${dataset}. \n\nDo you want to continue?`
      }
      const response = dialog.showMessageBoxSync(options);
      if (response == 0){
        client.invoke("grant_access", username, password, hostname, dataset, requester, expiryDate, function(error, res, more) {
          if (success){
            notifier.notify({"title" : "FRDR-Crypto", "message" : "Access Granted"});
          } else {
            notifier.notify({"title" : "FRDR-Crypto", "message" : `Error granting access. ${result}`});
          }
        });
      }
    }
    else {
      notifier.notify({"title" : "FRDR-Crypto", "message" : `Error finding the User in Vault. \n${result}`});
    }
  });
}

function reviewShares() {
  var hostname = document.getElementById("hostname").value;
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;
  client.invoke("create_access_granter", username, password, hostname, function(error, res, more) {
    var success = res[0];
    var errMessage = res[1];
    if (success) {
      var window = remote.getCurrentWindow();
      var reviewWindow = new remote.BrowserWindow({
        parent: window, 
        show: false, 
        width: 600, 
        height: 500,       
        webPreferences: {
          nodeIntegration: true
        }
      });
      reviewWindow.setMenuBarVisibility(false);
      reviewWindow.loadURL(require('url').format({
        pathname: path.join(__dirname, 'indexReview.html'),
        protocol: 'file:',
        slashes: true
      }));
      reviewWindow.once('ready-to-show', () => {
        reviewWindow.show()
      });
    }
    else {
      notifier.notify({"title" : "FRDR-Crypto", "message" : `Error reviewing shares. \n${errMessage}`});
    }
  });
}

document.getElementById("ReviewShares").addEventListener("click", reviewShares);

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

