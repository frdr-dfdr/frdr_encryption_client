const {ipcRenderer} = require('electron');

function contactus() {
  ipcRenderer.send("contact-us", $.i18n().locale);
}

document.getElementById("contactus").addEventListener("click", contactus);

