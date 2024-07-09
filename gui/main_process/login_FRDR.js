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

const {ipcMain} = require('electron');
const {sendMessage} = require('../main.js');

ipcMain.on('login-frdr-api-globus', async (event, loginSuccessMsg) => {
  const { result } = await sendMessage("login_frdr_api_globus", [loginSuccessMsg]);
  var successLogin = result[0];
  var errMessageLogin = result[1];
  if (successLogin) {
    event.reply('notify-login-frdr-done');
  }
  else {
    event.reply('notify-login-frdr-error', errMessageLogin);
  }
});