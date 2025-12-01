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

const {ipcRenderer} = require('electron');

function transferOwnership() {
  var dataset = document.getElementById("dataset").value.trim();
  var new_owner = document.getElementById("new_owner").value.trim();
  var dialogOptions = {
    type: "question",
    buttons: [$.i18n("app-transfer-ownership-confirm-btn1"), $.i18n("app-transfer-ownership-confirm-btn2")],
    defaultId: 1,
    title: "Confirmation",
    message: $.i18n("app-transfer-ownership-confirm")
  };
  ipcRenderer.send("transfer-ownership", new_owner, dataset, dialogOptions);
}

ipcRenderer.on('notify-get-entity-name-error', function (_event, result) {
  alert($.i18n('app-transfer-ownership-find-user-error', result), "");
});

ipcRenderer.on('notify-get-dataset-title-error', function (_event, result) {
  alert($.i18n('app-transfer-ownership-find-dataset-error', result), "");
});

ipcRenderer.on('notify-transfer-ownership-done', function (_event) {
  alert($.i18n('app-transfer-ownership-done'), "");
  ipcRenderer.send('transfer-ownership-done-show-next-step');
});

ipcRenderer.on('notify-transfer-ownership-error', function (_event, errMessage) {
  alert($.i18n('app-transfer-ownership-error', errMessage), "");
});

$('#transfer_ownership').on("click", function(){
  if ($("#dataset").val() == "") {
    alert($.i18n('app-transfer-ownership-dataset-missing'));
  }
  else if ($("#new_owner").val() == "") {
    alert($.i18n('app-transfer-ownership-new-owner-missing'));
  }
  else {
    transferOwnership();
  }
});