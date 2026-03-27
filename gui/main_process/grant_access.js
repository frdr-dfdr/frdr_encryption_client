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

ipcMain.on('get-pending-grant-access-requests', async (event) => {
  try {
    const { result } = await sendMessage("get_pending_grant_access_requests", []);
    var success = result[0];
    var requests = result[1];
    if (success) {
      event.reply('notify-pending-grant-access-requests', requests);
    } else {
      event.reply('notify-pending-grant-access-requests-error');
    }
  } catch (e) {
    event.reply('notify-pending-grant-access-requests-error');
  }
});

ipcMain.on('grant-access', async (event, req, dialogOptions) => {
  const datasetTitle = req.title || req.vault_dataset_id;
  const requesterDisplay = req.requester_name
    ? `${req.requester_name} (${req.requester_email})`
    : req.requester_email || req.vault_requester_id;

  dialogOptions['message'] = dialogOptions['message']
    .replace("$1", requesterDisplay)
    .replace("$2", datasetTitle);

  const response = dialog.showMessageBoxSync(dialogOptions);
  if (response !== 0) return;

  event.reply('notify-grant-access-started');

  const { result } = await sendMessage("grant_access", [req.vault_dataset_id, req.vault_requester_id]);
  var success = result[0];
  var errMessage = result[1];

  if (success) {
    event.reply('notify-grant-access-done');
  } else {
    event.reply('notify-grant-access-error', req.vault_dataset_id, req.vault_requester_id, errMessage);
  }
});

ipcMain.on('grant-access-done-show-next-step', (_event) => {
  var currentWindow = BrowserWindow.getFocusedWindow();
  currentWindow.loadURL(require('url').format({
    pathname: path.join(__dirname, '../pages/grant-access-done.html'),
    protocol: 'file:',
    slashes: true
  }));

  currentWindow.once('ready-to-show', () => {
    currentWindow.show()
  });
});

ipcMain.on('show-error-dialog', (_event, message) => {
  dialog.showMessageBoxSync({
    type: 'error',
    title: 'Error',
    message: message
  });
});