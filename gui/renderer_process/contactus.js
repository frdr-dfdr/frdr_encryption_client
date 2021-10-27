const {ipcRenderer} = require('electron');
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

function contactus() {
  var contactURL = "";
  try {
    var configPath = "";
    if (process.env.NODE_ENV == "development") {
      configPath = path.join(__dirname, '..', '..','config', 'config.yml');
    }
    else {
      var configPath = path.join(__dirname, '..', 'app_gui','config', 'config.yml');
    }
    let fileContents = fs.readFileSync(configPath, 'utf8');
    let config = yaml.load(fileContents);
    contactURL = config["FRDR_CONTACTUS_URL"];
  } catch (e) {
    console.log(e);
  }
  ipcRenderer.send("contact-us", contactURL + $.i18n().locale);
}

document.getElementById("contactus").addEventListener("click", contactus);

