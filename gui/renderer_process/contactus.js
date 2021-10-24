const {ipcRenderer} = require('electron');
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

function contactus() {
  var contactURL = "";
  try {
    let fileContents = fs.readFileSync(path.join(__dirname, '../../config/config.yml'), 'utf8');
    let config = yaml.load(fileContents);
    contactURL = config["FRDR_CONTACTUS_URL"];
  } catch (e) {
    console.log(e);
  }
  ipcRenderer.send("contact-us", contactURL + $.i18n().locale);
}

document.getElementById("contactus").addEventListener("click", contactus);

