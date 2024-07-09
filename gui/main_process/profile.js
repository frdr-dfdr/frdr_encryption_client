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

const {ipcMain} = require('electron');
const {sendMessage} = require('../main.js');
 
ipcMain.on('get-entity-id', async (event) => {
  const {result} = await sendMessage("get_entity_id");
  var success = result[0];
  var entity_id_result = result[1];
  if (success && entity_id_result != null) {
    event.reply('notify-get-entity-id-done', entity_id_result);
    const {result: get_entity_name_result} = await sendMessage("get_entity_name", [entity_id_result])
    var success = get_entity_name_result[0];
    var entity_name_result = get_entity_name_result[1];
    if (success && entity_name_result != null) {
      event.reply('notify-get-entity-name-done', entity_name_result);
    }
    else {
      event.reply('notify-get-entity-name-error', entity_name_result);
    }
  }
  else {
    event.reply('notify-get-entity-id-error', entity_id_result);
  }
});
