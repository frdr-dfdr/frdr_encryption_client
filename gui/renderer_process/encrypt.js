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

var dashboardURL = null;

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
  dashboardURL = config["FRDR_DEPOSIT_DASHBOARD_URL"];
} catch (e) {
  // log error, the link to FRDR profile page is not working
  console.log(e);
}

let input_path = null;
let output_path = null;

// Send a open directory selector dialog message from a renderer process to main process 
$('#input_path_dir').on("click", function(){
  ipcRenderer.send('encrypt-open-input-dir-dialog');
});

//Getting back the information after selecting the dir
ipcRenderer.on('encrypt-selected-input-dir', function (_event, path) {
  //print the path selected
  input_path = path;
  document.getElementById('selected-input-dir').innerHTML = $.i18n('app-encrypt-selected', path);
});

// Send a open directory selector dialog message from a renderer process to main process 
$('#output_path_dir').on("click", function(){
  ipcRenderer.send('encrypt-open-output-dir-dialog')
});

//Getting back the information after selecting the dir
ipcRenderer.on('encrypt-selected-output-dir', function (_event, path) {
  //print the path selected
  output_path = path;
  document.getElementById('selected-output-dir').innerHTML = $.i18n('app-encrypt-selected', path);
});

ipcRenderer.on('notify-encrypt-done', function (_event, result) {
  alert($.i18n('app-encrypt-done', result), "");
  ipcRenderer.send('encrypt-done-show-next-step');
});

ipcRenderer.on('notify-encrypt-error', function (_event, result) {
  alert($.i18n('app-encrypt-error', result), "");
});

$('#encrypt').on("click", function(){
  if (input_path == null){
      alert($.i18n('app-encrypt-input-missing'));
  }
  else if (output_path == null) {
    alert($.i18n('app-encrypt-output-missing'));
  }
  else {
    var options = {
      type: "question",
      buttons: [$.i18n("app-encrypt-confirm-btn1"), $.i18n("app-encrypt-confirm-btn2")],
      defaultId: 1,
      title: "Confirmation",
      message: $.i18n("app-encrypt-confirm")
    }
    ipcRenderer.send("encrypt", input_path[0], output_path[0], options);
  }
});

$('#encrypt-cancel').on("click", function(){
    ipcRenderer.send("encrypt-cancel");
});

ipcRenderer.on('notify-encrypt-cancel-error', function (_event, result) {
  alert($.i18n('app-encrypt-cancel-error', result), "");
});

function openFRDRDepositDashboard() {
  shell.openExternal(dashboardURL);
}

document.getElementById("open-frdr-dashboard").addEventListener("click", openFRDRDepositDashboard);