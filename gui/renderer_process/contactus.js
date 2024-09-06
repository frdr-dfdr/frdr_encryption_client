/*
 *   Copyright (c) 2024 Digital Research Alliance of Canada
 *  
 *   This file is part of FRDR Encryption Application.
 *  
 *   FRDR Encryption Application is free software: you can redistribute it
 *   and/or modify it under the terms of the GNU General Public License as
 *   published by the FRDR Encryption Application Software Foundation,
 *   either version 3 of the License, or (at your option) any later version.
 *  
 *   FRDR Encryption Application is distributed in the hope that it will be
 *   useful, but WITHOUT ANY WARRANTY; without even the implied
 *   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 *   PURPOSE. See the GNU General Public License for more details.
 *  
 *   You should have received a copy of the GNU General Public License
 *   along with FRDR Encryption Application. If not, see <https://www.gnu.org/licenses/>.
 */

function contactus() {
  var contactURL = "";
  try {
    var configPath = "";
    if (process.env.NODE_ENV == "development") {
      configPath = path.join(__dirname, '..', '..','config', 'config.yml');
    }
    else if (process.platform === 'win32') {
      configPath = path.join(__dirname, '..', 'app_gui', 'config', 'config.yml');
    }
    else {
      configPath = path.join(__dirname, '..', 'app_gui', '_internal', 'config', 'config.yml');
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

