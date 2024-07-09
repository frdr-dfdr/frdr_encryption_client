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
 *   along with Foobar. If not, see <https://www.gnu.org/licenses/>.
 */

const {ipcRenderer} = require('electron');

function grantAccess() {
  var dataset = document.getElementById("dataset").value.trim();
  var requester = document.getElementById("requester").value.trim();
  var dialogOptions = {
    type: "question",
    buttons: [$.i18n("app-grant-access-confirm-btn1"), $.i18n("app-grant-access-confirm-btn2")],
    defaultId: 1,
    title: "Confirmation",
    message: $.i18n("app-grant-access-confirm")
  };
  ipcRenderer.send("grant-access", requester, dataset, dialogOptions);
}

ipcRenderer.on('notify-get-entity-name-error', function (_event, result) {
  alert($.i18n('app-grant-access-find-user-error', result), "");
});

ipcRenderer.on('notify-get-dataset-title-error', function (_event, result) {
  alert($.i18n('app-grant-access-find-dataset-error', result), "");
});

ipcRenderer.on('notify-grant-access-done', function (_event) {
  alert($.i18n('app-grant-access-done'), "");
  ipcRenderer.send('grant-access-done-show-next-step');
});

ipcRenderer.on('notify-grant-access-error', function (_event, errMessage) {
  alert($.i18n('app-grant-access-error', errMessage), "");
});

$('#grant_access').on("click", function(){
  if ($("#dataset").val() == "") {
    alert($.i18n('app-grant-access-dataset-missing'));
  }
  else if ($("#requester").val() == "") {
    alert($.i18n('app-grant-access-requester-missing'));
  }
  else {
    grantAccess();
  }
});