const remote = require('electron').remote;

function contactus() {
  const win = new remote.BrowserWindow({width: 800, height: 600});
  win.loadURL("https://www.frdr-dfdr.ca/repo/contactus");
}

document.getElementById("contactus").addEventListener("click", contactus);

