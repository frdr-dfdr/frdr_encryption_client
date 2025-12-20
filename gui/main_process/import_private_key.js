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

const {ipcMain, dialog} = require('electron');
const fs = require('fs').promises;
const {sendMessage} = require('../main.js');

ipcMain.on('import-private-key-select-file', async (event) => {
  
  try {
    const result = await dialog.showOpenDialog({
      title: 'Select Private Key File',
      properties: ['openFile'],
      filters: [
        { name: 'PEM Files', extensions: ['pem', 'key'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (result.canceled || result.filePaths.length === 0) {
      event.reply('notify-import-private-key-cancelled');
      return;
    }

    const keyPath = result.filePaths[0];
    event.reply('notify-import-private-key-file-selected', keyPath);
    
  } catch (error) {
    event.reply('notify-import-private-key-error', error.message);
  }
});

ipcMain.on('import-private-key', async (event, data) => {
  
  try {
    var hasFile = data.filePath !== null && data.filePath !== undefined;
    var hasText = data.textContent !== null && data.textContent !== undefined;
    
    // Case 1: Only file provided
    if (hasFile && !hasText) {
      const { result } = await sendMessage("import_private_key_from_file", [data.filePath]);
      var success = result[0];
      var message = result[1];
      
      if (success) {
        event.reply('notify-import-private-key-success', message);
      } else {
        event.reply('notify-import-private-key-error', message);
      }
    }
    // Case 2: Only text provided
    else if (!hasFile && hasText) {
      const { result } = await sendMessage("import_private_key_from_text", [data.textContent]);
      var success = result[0];
      var message = result[1];
      
      if (success) {
        event.reply('notify-import-private-key-success', message);
      } else {
        event.reply('notify-import-private-key-error', message);
      }
    }
    // Case 3: Both file and text provided - need to verify they match
    else if (hasFile && hasText) {
      // Read the file content
      const fileContent = await fs.readFile(data.filePath, 'utf8');
      
      // Normalize whitespace for comparison
      const normalizeKey = (key) => key.trim().replace(/\s+/g, '\n');
      const normalizedFile = normalizeKey(fileContent);
      const normalizedText = normalizeKey(data.textContent);
      
      if (normalizedFile === normalizedText) {
        const { result } = await sendMessage("import_private_key_from_file", [data.filePath]);
        var success = result[0];
        var message = result[1];
        
        if (success) {
          event.reply('notify-import-private-key-success', message);
        } else {
          event.reply('notify-import-private-key-error', message);
        }
      } else {
          event.reply('notify-import-private-key-error', 'app-import-key-error-mismatch');
      }
    }
    // Case 4: Neither provided (shouldn't happen due to frontend validation)
    else {
      event.reply('notify-import-private-key-error', 'app-import-key-error-no-input');
    }
    
  } catch (error) {
    event.reply('notify-import-private-key-error', error.message);
  }
});