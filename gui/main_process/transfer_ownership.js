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

ipcMain.on('get-pending-key-transfers', async (event) => {
  try {
    const {result} = await sendMessage("get_pending_key_transfers", []);
    var success = result[0];
    var transfers = result[1];
    if (success) {
      event.reply('notify-pending-key-transfers', transfers);
    } else {
      event.reply('notify-pending-key-transfers-error');
    }
  } catch (e) {
    event.reply('notify-pending-key-transfers-error');
  }
});

ipcMain.on('transfer-ownership', async (event, req, dialogOptions) => {
  // req already has titles and IDs from the API, no need to call get_request_info
  const isBulk = req.items.length > 1;
  const datasetDisplay = isBulk
    ? req.items.map(i => i.title || i.vault_dataset_id).join(', ')
    : (req.items[0].title || req.items[0].vault_dataset_id);

  dialogOptions['message'] = dialogOptions['message']
    .replaceAll("$1", req.recipient_email)
    .replace("$2", datasetDisplay)
    .replaceAll("$3", req.recipient_name);

  const response = dialog.showMessageBoxSync(dialogOptions);
  if (response !== 0) return;

  event.reply('notify-transfer-ownership-started', req.request_id);

  // For bulk, transfer each dataset sequentially
  for (const item of req.items) {
    const {result} = await sendMessage("transfer_ownership", [req.request_id, item.vault_dataset_id, req.vault_recipient_id]);
    var success = result[0];
    var errMessage = result[1];
    if (!success) {
      event.reply('notify-transfer-ownership-error', req.request_id, errMessage);
      return;
    }
  }
  event.reply('notify-transfer-ownership-done');
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