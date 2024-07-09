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

const {BrowserWindow, dialog, ipcMain, shell, app} = require('electron');
const path = require('path');
const fs = require('fs');
const {sendMessage} = require('../main.js');

var basepath = app.getPath("userData");

// Main process to open a folder selector dialog
ipcMain.on('encrypt-open-input-dir-dialog', function (event) {
  var selected_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
  if (selected_path) {
    event.reply('encrypt-selected-input-dir', selected_path);
  }
})

ipcMain.on('encrypt-open-output-dir-dialog', function (event) {
  var selected_path = dialog.showOpenDialogSync({properties: ['openDirectory']});
  if (selected_path) {
    event.reply('encrypt-selected-output-dir', selected_path);
  }
})

ipcMain.on('encrypt', async (event, input_path, output_path, options) => {
  var response = dialog.showMessageBoxSync(options);
  if (response == 0) {
    var childWindow = new BrowserWindow({ 
      parent: BrowserWindow.getFocusedWindow(), 
      modal: true, 
      show: false, 
      width: 400, 
      height: 200, 
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false
      }
    });
    childWindow.loadURL(require('url').format({
      pathname: path.join(__dirname, '../pages/encrypt-in-progress.html'),
      protocol: 'file:',
      slashes: true
    }));
    childWindow.once('ready-to-show', () => {
      childWindow.show()
    });

    const { result } = await sendMessage("encrypt", [input_path, output_path]);
    var success = result[0];
    var message = result[1];
    if (message != "") {
      childWindow.close();
    }
    if (success){
      event.reply('notify-encrypt-done', message);
      shell.showItemInFolder(message);
    } else {
      event.reply('notify-encrypt-error', message);
    }
  }
});

ipcMain.on('encrypt-cancel', (event) => {
  try {
    const pid = fs.readFileSync(path.join(basepath, 'pid'), 'utf8');
    process.kill(pid);
  } catch (err) {
    event.reply('notify-encrypt-cancel-error', err);
  }
});

ipcMain.on('encrypt-done-show-next-step', (_event) => {
  var currentWindow = BrowserWindow.getFocusedWindow();
  currentWindow.loadURL(require('url').format({
    pathname: path.join(__dirname, '../pages/encrypt-done.html'),
    protocol: 'file:',
    slashes: true
  }));

  currentWindow.once('ready-to-show', () => {
    currentWindow.show()
  });
});