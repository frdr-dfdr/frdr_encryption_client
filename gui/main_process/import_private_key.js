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
const {sendMessage} = require('../main.js');
const Seven = require('node-7z');
const sevenBin = require('7zip-bin');
const path = require('path');
const fs = require('fs').promises;
const os = require('os');

// Select ZIP file
ipcMain.on('import-private-key-select-zip', async (event) => {
  try {
    const result = await dialog.showOpenDialog({
      title: 'Select Protected ZIP File',
      properties: ['openFile'],
      filters: [
        { name: 'ZIP Files', extensions: ['zip'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (result.canceled || result.filePaths.length === 0) {
      event.reply('notify-import-private-key-cancelled');
      return;
    }

    const zipPath = result.filePaths[0];
    event.reply('notify-import-private-key-zip-selected', zipPath);
    
  } catch (error) {
    event.reply('notify-import-private-key-error', error.message);
  }
});

ipcMain.on('import-private-key-from-zip', async (event, data) => {
  try {
    const { zipPath, password } = data;
    
    // Create a temporary directory for extraction
    const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'key-import-'));
    
    const extractStream = Seven.extractFull(zipPath, tempDir, {
      password: password,
      $bin: sevenBin.path7za
    });
    
    extractStream.on('end', async () => {
      try {
        // Find .pem file in extracted files
        const files = await fs.readdir(tempDir);
        const pemFile = files.find(file => file.endsWith('.pem'));
        
        if (!pemFile) {
          // Clean up
          await fs.rm(tempDir, { recursive: true, force: true });
          event.reply('notify-import-private-key-error', 'app-import-key-error-no-pem-in-zip');
          return;
        }
        
        const keyPath = path.join(tempDir, pemFile);
        const keyContent = await fs.readFile(keyPath, 'utf8');
        
        // Clean up temp directory
        await fs.rm(tempDir, { recursive: true, force: true });
        
        const { result } = await sendMessage("import_private_key_from_text", [keyContent]);
        const success = result[0];
        const message = result[1];
        
        if (success) {
          event.reply('notify-import-private-key-success', message);
        } else {
          event.reply('notify-import-private-key-error', message);
        }
      } catch (error) {
        await fs.rm(tempDir, { recursive: true, force: true }).catch(() => {});
        event.reply('notify-import-private-key-error', error.message);
      }
    });
    
    extractStream.on('error', async (err) => {
      // Clean up
      await fs.rm(tempDir, { recursive: true, force: true }).catch(() => {});
      
      // Check if it's a password error
      if (err.message.includes('Wrong password') || err.message.includes('Can not open encrypted archive')) {
        event.reply('notify-import-private-key-error', 'app-import-key-error-wrong-password');
      } else {
        event.reply('notify-import-private-key-error', err.message);
      }
    });
    
  } catch (error) {
    event.reply('notify-import-private-key-error', error.message);
  }
});

ipcMain.on('import-private-key-select-and-import-file', async (event) => {
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
    
    const { result: importResult } = await sendMessage("import_private_key_from_file", [keyPath]);
    var success = importResult[0];
    var message = importResult[1];
    
    if (success) {
      event.reply('notify-import-private-key-success', message);
    } else {
      event.reply('notify-import-private-key-error', message);
    }
    
  } catch (error) {
    event.reply('notify-import-private-key-error', error.message);
  }
});

ipcMain.on('import-private-key-from-text', async (event, keyText) => {
  try {
    const { result } = await sendMessage("import_private_key_from_text", [keyText]);
    var success = result[0];
    var message = result[1];
    
    if (success) {
      event.reply('notify-import-private-key-success', message);
    } else {
      event.reply('notify-import-private-key-error', message);
    }
    
  } catch (error) {
    event.reply('notify-import-private-key-error', error.message);
  }
});