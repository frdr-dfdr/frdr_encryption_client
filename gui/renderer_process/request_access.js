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

const {ipcRenderer, shell} = require('electron');
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

var profileURL = null;

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
  profileURL = config["FRDR_PROFILE_URL"];
} catch (e) {
  // log error, the link to FRDR profile page is not working
  console.log(e);
}

function generateAccessRequest() {
  var dialogOptions = {
    type: 'question',
    buttons: [$.i18n("app-request-access-confirm-btn")],
    defaultId: 0,
    title: 'Question',
    message: $.i18n("app-request-access-confirm-msg"),
  };

  var copiedDoneDialogOptions = {
    type: "info",
    buttons: [$.i18n("app-request-access-ok-btn")],
    title: "Important Information",
    message: $.i18n('app-request-access-done-msg')
  }

  ipcRenderer.send("request-access", dialogOptions, copiedDoneDialogOptions);
}

document.getElementById("request-access").addEventListener("click", generateAccessRequest);

ipcRenderer.on('notify-request-access-error', function (_event, result) {
  alert($.i18n('app-request-access-error', result), "");
});

function openFRDRProfile() {
  shell.openExternal(profileURL);
}

document.getElementById("open-frdr-profile").addEventListener("click", openFRDRProfile);