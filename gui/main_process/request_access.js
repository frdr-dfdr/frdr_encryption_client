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

const {dialog, ipcMain, clipboard} = require('electron');
const {sendMessage} = require('../main.js');

ipcMain.on('request-access', async (event, dialogOptions, copiedDoneDialogOptions) => {
  const {result} = await sendMessage("get_entity_id");
  var success = result[0];
  var message = result[1];
  if (success) {
    dialogOptions['detail'] = message;
    const response = dialog.showMessageBoxSync(dialogOptions);
    if (response == 0) {
      clipboard.writeText(message);
      dialog.showMessageBoxSync(copiedDoneDialogOptions);
    }
  }
  else {
    event.reply('notify-request-access-error', message);
  }
});