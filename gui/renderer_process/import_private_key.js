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

var selectedZipPath = null;

// Import from ZIP - select file and show password modal
$('#import-from-zip-btn').on("click", function(){
  ipcRenderer.send('import-private-key-select-zip');
});

// Import from PEM file - select and import directly
$('#import-from-file-btn').on("click", function(){
  ipcRenderer.send('import-private-key-select-and-import-file');
});

// Import from text
$('#import-from-text-btn').on("click", function(){
  var keyText = document.getElementById('key-text-input').value.trim();
  
  if (!keyText) {
    alert($.i18n('app-import-key-error-no-input'));
    return;
  }
  
  // Basic validation for text input
  if (!keyText.includes('BEGIN') || !keyText.includes('PRIVATE KEY')) {
    alert($.i18n('app-import-key-error-invalid-format'));
    return;
  }
  
  ipcRenderer.send('import-private-key-from-text', keyText);
});

// Show/hide ZIP password
document.getElementById('show-zip-password-checkbox').addEventListener('change', (e) => {
  const passwordInput = document.getElementById('zip-password');
  passwordInput.type = e.target.checked ? 'text' : 'password';
});

$('#zipPasswordModal').on('hidden.bs.modal', function () {
  document.getElementById('zip-password').value = '';
  document.getElementById('show-zip-password-checkbox').checked = false;
  document.getElementById('zip-modal-error-message').style.display = 'none';
});

// Confirm import from ZIP
document.getElementById('confirm-import-zip-btn').addEventListener('click', () => {
  const password = document.getElementById('zip-password').value;
  
  document.getElementById('zip-modal-error-message').style.display = 'none';
  
  if (!password) {
    showZipModalError($.i18n('app-import-key-zip-error-no-password'));
    return;
  }
  
  $('#zipPasswordModal').modal('hide');
  
  ipcRenderer.send('import-private-key-from-zip', {
    zipPath: selectedZipPath,
    password: password
  });
});

$('#cancel-import-btn').on("click", function(){
  window.location.href = './local-keys-error.html';
});

ipcRenderer.on('notify-import-private-key-zip-selected', function (_event, zipPath) {
  selectedZipPath = zipPath;
  document.getElementById('selected-zip-path').innerHTML = zipPath;
  
  $('#zipPasswordModal').modal('show');
});

ipcRenderer.on('notify-import-private-key-file-selected', function (_event, filePath) {
  document.getElementById('selected-file-path').innerHTML = filePath;
});

ipcRenderer.on('notify-import-private-key-success', function (_event, message) {
  alert($.i18n('app-import-key-success'));
  
  // Clear form
  document.getElementById('key-text-input').value = '';
  document.getElementById('selected-file-path').innerHTML = '';
  document.getElementById('selected-zip-path').innerHTML = '';
  selectedZipPath = null;
  
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
  document.getElementById('selected-zip-path').innerHTML = '';
  selectedZipPath = null;
});

// Helper function to show ZIP modal error
function showZipModalError(message) {
  const errorDiv = document.getElementById('zip-modal-error-message');
  const errorText = document.getElementById('zip-modal-error-text');
  errorText.textContent = message;
  errorDiv.style.display = 'block';
}