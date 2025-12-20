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

const {ipcRenderer} = require('electron');

var selectedFilePath = null;

$('#import-from-file-btn').on("click", function(){
  ipcRenderer.send('import-private-key-select-file');
});

$('#import-btn').on("click", function(){
  var keyText = document.getElementById('key-text-input').value.trim();
  
  var hasFile = selectedFilePath !== null;
  var hasText = keyText.length > 0;
  
  if (!hasFile && !hasText) {
    alert($.i18n('app-import-key-error-no-input'));
    return;
  }
  
  // Basic validation for text input
  if (hasText && (!keyText.includes('BEGIN') || !keyText.includes('PRIVATE KEY'))) {
    alert($.i18n('app-import-key-error-invalid-format'));
    return;
  }
  
  ipcRenderer.send('import-private-key', {
    filePath: selectedFilePath,
    textContent: hasText ? keyText : null
  });
});

$('#cancel-import-btn').on("click", function(){
  window.location.href = './local-keys-error.html';
});

ipcRenderer.on('notify-import-private-key-file-selected', function (_event, filePath) {
  selectedFilePath = filePath;
  document.getElementById('selected-file-path').innerHTML = filePath;
});

ipcRenderer.on('notify-import-private-key-success', function (_event, message) {
  alert($.i18n('app-import-key-success'));
  
  // Clear form
  document.getElementById('key-text-input').value = '';
  document.getElementById('selected-file-path').innerHTML = '';
  selectedFilePath = null;
  
  // Redirect after user clicks OK
  window.location.href = './home.html';
});

ipcRenderer.on('notify-import-private-key-error', (event, errMessage) => {
  // Check if it's an i18n key or raw error message
  let displayMessage;
  if (errMessage.startsWith('app-import-key-')) {
    displayMessage = $.i18n(errMessage);
  } else {
    // It's a raw error message
    displayMessage = $.i18n('app-import-key-error-generic', errMessage);
  }
  
  alert(displayMessage);
});

ipcRenderer.on('notify-import-private-key-cancelled', function (_event) {
  document.getElementById('selected-file-path').innerHTML = '';
  selectedFilePath = null;
});