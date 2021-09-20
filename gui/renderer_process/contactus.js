const {ipcRenderer} = require('electron');

function contactus() {
  ipcRenderer.send("contact-us");
}

document.getElementById("contactus").addEventListener("click", contactus);

