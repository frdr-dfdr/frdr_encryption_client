const { ipcMain, dialog } = require('electron');
const { sendMessage } = require('../main.js');
const fs = require('fs');
const archiver = require('archiver');

// Register the encrypted format
archiver.registerFormat('zip-encrypted', require('archiver-zip-encrypted'));

ipcMain.on('get-private-key-location', async (event) => {
  try {
    const { result } = await sendMessage("get_private_key_path");
    const keyPath = result;
    event.reply('notify-private-key-location', keyPath);
  } catch (error) {
    event.reply('notify-export-private-key-error', error.message);
  }
});

ipcMain.on('get-private-key-content', async (event) => {
  try {
    const { result } = await sendMessage("get_private_key_content");
    const keyContent = result;
    event.reply('notify-private-key-content', keyContent);
  } catch (error) {
    event.reply('notify-export-private-key-error', error.message);
  }
});

// Export private key to password-protected ZIP
ipcMain.on('export-private-key-to-file', async (event, password) => {
  try {

    // Get user entity id and key content 
    const { result } = await sendMessage("get_export_key_info");
    const uuid = result[0];
    const keyContent = result[1];
    
    // Generate default filename with entity id
    const defaultFilename = uuid ? `private_key_${uuid}_protected.zip`: 'private_key_protected.zip';

    const { filePath, canceled } = await dialog.showSaveDialog({
      title: 'Export Private Key',
      defaultPath: defaultFilename,
      filters: [
        { name: 'ZIP Files', extensions: ['zip'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
    
    if (canceled || !filePath) {
      return;
    }
    
    // Export as password-protected ZIP
    await exportAsEncryptedZip(keyContent, filePath, password, uuid);
    
    event.reply('notify-export-private-key-success', filePath);
  } catch (error) {
    event.reply('notify-export-private-key-error', error.message);
  }
});

// Export as password-protected ZIP
async function exportAsEncryptedZip(keyContent, outputPath, password, uuid) {
  return new Promise((resolve, reject) => {
    const output = fs.createWriteStream(outputPath);
    const archive = archiver('zip-encrypted', {
      zlib: { level: 8 },
      encryptionMethod: 'aes256',
      password: password
    });

    output.on('error', (err) => {
      reject(err);
    });
    
    output.on('close', () => {
      resolve();
    });
    
    archive.on('error', (err) => {
      reject(err);
    });

    archive.on('warning', (err) => {
      if (err.code === 'ENOENT') {
        console.warn('Archive warning:', err);
      } else {
        reject(err);
      }
    });
    
    archive.pipe(output);

    const pemFilename = uuid ? `private_key_${uuid}.pem` : 'private_key.pem';
    
    archive.append(keyContent, { name: pemFilename });
  
    archive.finalize();
  });
}