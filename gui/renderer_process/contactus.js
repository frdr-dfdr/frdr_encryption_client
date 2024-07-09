/*
 *   Copyright (c) 2024 Digital Research Alliance of Canada
 *  
 *   This file is part of FRDR Encryption Application.
 *  
 *   FRDR Encryption Application is free software: you can redistribute it
 *   and/or modify it under the terms of the GNU General Public License as
 *   published by the FRDR Encryption Application Software Foundation,
 *   version 3 of the License.
 *  
 *   FRDR Encryption Application is distributed in the hope that it will be
 *   useful, but WITHOUT ANY WARRANTY; without even the implied
 *   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 *   PURPOSE. See the GNU General Public License for more details.
 *  
 *   You should have received a copy of the GNU General Public License
 *   along with Foobar. If not, see <https://www.gnu.org/licenses/>.
 */

if (typeof ipcRenderer == 'undefined') {
  const {ipcRenderer} = require('electron');
}

if (typeof fs == 'undefined') {
  const fs = require('fs');
}

if (typeof yaml == 'undefined') {
  const yaml = require('js-yaml');
}

if (typeof path == 'undefined') {
  const path = require('path');
}

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

