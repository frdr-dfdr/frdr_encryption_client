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

const {BrowserWindow, dialog, ipcMain} = require('electron');
const path = require('path');
const {sendMessage} = require('../main.js');

ipcMain.on('transfer-ownership', async(event, new_owner, dataset, dialogOptions) => {
  const {result} = await sendMessage("get_request_info", [new_owner, dataset]);
  var entity_success = result[0];
  var entity_result = result[1];
  var dataset_success = result[2];
  var dataset_result = result[3];
  if (entity_success && entity_result != null && dataset_success) {
    dialogOptions['message'] = dialogOptions['message'].replaceAll("$1", entity_result).replace("$2", dataset_result);
    const response = dialog.showMessageBoxSync(dialogOptions);
    if (response == 0) {
      const {result: transfer_ownership_result} = await sendMessage("transfer_ownership", [dataset, new_owner])
      var successTransferOwnership = transfer_ownership_result[0];
      var errMessageTransferOwnership = transfer_ownership_result[1];
      if (successTransferOwnership){
        event.reply('notify-transfer-ownership-done');
      } else {
        event.reply('notify-transfer-ownership-error', errMessageTransferOwnership);
      }
    }
  }
  else if (!entity_success || entity_result == null){
    event.reply('notify-get-entity-name-error', entity_result);
  }
  else if (!dataset_success){
    event.reply('notify-get-dataset-title-error', dataset_result);
  }
});

ipcMain.on('transfer-ownership-done-show-next-step', (_event) => {
  var currentWindow = BrowserWindow.getFocusedWindow();
  currentWindow.loadURL(require('url').format({
    pathname: path.join(__dirname, '../pages/transfer-ownership-done.html'),
    protocol: 'file:',
    slashes: true
  }));

  currentWindow.once('ready-to-show', () => {
    currentWindow.show()
  });
});