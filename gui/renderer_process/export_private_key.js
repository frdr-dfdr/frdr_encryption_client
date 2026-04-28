const { ipcRenderer, clipboard, shell } = require('electron');

let clipboardTimeout = null;
let isLocationVisible = false;

document.getElementById('show-password-checkbox').addEventListener('change', (e) => {
  const passwordInput = document.getElementById('export-password');
  const confirmInput = document.getElementById('export-password-confirm');
  const type = e.target.checked ? 'text' : 'password';
  passwordInput.type = type;
  confirmInput.type = type;
});

// Called on every keystroke in the confirm field, clears the error
function checkPasswordMatch() {
  const confirm = document.getElementById('export-password-confirm').value;
  const msg = document.getElementById('password-mismatch-msg');
  const confirmInput = document.getElementById('export-password-confirm');

  // If the user clears the field, reset validation state
  if (confirm.length === 0) {
    msg.style.display = 'none';
    confirmInput.classList.remove('is-invalid');
  }
}

// Called when the confirm field loses focus, shows the mismatch error
function validatePasswordMatch() {
  const password = document.getElementById('export-password').value;
  const confirm  = document.getElementById('export-password-confirm').value;
  const msg = document.getElementById('password-mismatch-msg');
  const confirmInput = document.getElementById('export-password-confirm');

  if (confirm.length === 0) return; // Don't validate an empty field on blur

  if (password !== confirm) {
    msg.style.display = 'block';
    confirmInput.classList.add('is-invalid');
  } else {
    msg.style.display = 'none';
    confirmInput.classList.remove('is-invalid');
  }
}

const confirmInput = document.getElementById('export-password-confirm');
const passwordInput = document.getElementById('export-password');

// Keystroke: only clears the error once the user fixes the mismatch
confirmInput.addEventListener('input', checkPasswordMatch);

// Blur: defers the mismatch error until the user leaves the field
confirmInput.addEventListener('blur', validatePasswordMatch);

// If the user edits the original password after confirm is already filled,
// re-validate immediately so the error state stays in sync
passwordInput.addEventListener('input', () => {
  if (confirmInput.value.length > 0) validatePasswordMatch();
});

document.getElementById('toggle-location-btn').addEventListener('click', () => {
  const locationDiv = document.getElementById('key-location');
  const toggleBtn = document.getElementById('toggle-location-btn');
  
  if (isLocationVisible) {
    // Hide location
    locationDiv.style.display = 'none';
    toggleBtn.setAttribute('data-i18n', 'app-export-key-show-location');
    toggleBtn.textContent = $.i18n('app-export-key-show-location');
    isLocationVisible = false;
  } else {
    // Show location
    if (!document.getElementById('key-location-path').value) {
      // Load the path
      toggleBtn.disabled = true;
      toggleBtn.setAttribute('data-i18n', 'app-export-key-location-loading');
      ipcRenderer.send('get-private-key-location');
    } else {
      // Already have the path
      locationDiv.style.display = 'block';
      toggleBtn.setAttribute('data-i18n', 'app-export-key-hide-location');
      toggleBtn.textContent = $.i18n('app-export-key-hide-location');
      isLocationVisible = true;
    }
  }
});

document.getElementById('copy-location-btn').addEventListener('click', () => {
  const locationPath = document.getElementById('key-location-path').value;
  clipboard.writeText(locationPath);
  alert($.i18n('app-export-key-location-copied'));
});

document.getElementById('open-folder-btn').addEventListener('click', () => {
  const locationPath = document.getElementById('key-location-path').value;
  shell.showItemInFolder(locationPath);
});

document.getElementById('reveal-key-btn').addEventListener('click', () => {
  const confirmed = confirm($.i18n('app-export-key-reveal-confirm'));
  
  if (confirmed) {
    ipcRenderer.send('get-private-key-content');
  }
});

document.getElementById('copy-key-btn').addEventListener('click', () => {
  const keyContent = document.getElementById('key-content-textarea').value;
  clipboard.writeText(keyContent);
  
  alert($.i18n('app-export-key-copied-clipboard'));
  
  // Auto-clear clipboard after 30 seconds
  if (clipboardTimeout) {
    clearTimeout(clipboardTimeout);
  }
  clipboardTimeout = setTimeout(() => {
    clipboard.clear();
  }, 30000);
});

document.getElementById('hide-key-btn').addEventListener('click', () => {
  document.getElementById('key-content-section').style.display = 'none';
  document.getElementById('key-content-textarea').value = '';
  document.getElementById('reveal-key-btn').style.display = 'block';
});

// Clear password modal when it's closed
$('#passwordModal').on('hidden.bs.modal', function () {
  document.getElementById('export-password').value = '';
  document.getElementById('export-password-confirm').value = '';
  document.getElementById('show-password-checkbox').checked = false;
  document.getElementById('modal-error-message').style.display = 'none';
  document.getElementById('password-mismatch-msg').style.display = 'none';
  document.getElementById('export-password-confirm').classList.remove('is-invalid');
});

// Confirm export from modal
document.getElementById('confirm-export-btn').addEventListener('click', () => {
  const password = document.getElementById('export-password').value;
  const confirmPassword = document.getElementById('export-password-confirm').value;
  
  // Hide modal error
  document.getElementById('modal-error-message').style.display = 'none';
  
  if (!password) {
    showModalError($.i18n('app-export-key-error-no-password'));
    return;
  }
  
  if (password.length < 12) {
    showModalError($.i18n('app-export-key-error-password-length'));
    return;
  }
  
  // Mismatch is surfaced in real time — block submit if still mismatched
  if (password !== confirmPassword) {
    return;
  }

  if (!isStrongPassword(password)) {
    showModalError($.i18n('app-export-key-error-password-weak'));
    return;
  }

  // All validations passed - close modal and start export
  $('#passwordModal').modal('hide');
  ipcRenderer.send('export-private-key-to-file', password);
});

ipcRenderer.on('notify-private-key-location', (event, locationPath) => {
  const locationDiv = document.getElementById('key-location');
  const toggleBtn = document.getElementById('toggle-location-btn');
  
  toggleBtn.disabled = false;
  
  document.getElementById('key-location-path').value = locationPath;
  locationDiv.style.display = 'block';
  toggleBtn.setAttribute('data-i18n', 'app-export-key-hide-location');
  toggleBtn.textContent = $.i18n('app-export-key-hide-location');
  isLocationVisible = true;
});

ipcRenderer.on('notify-private-key-content', (event, keyContent) => {
  document.getElementById('key-content-textarea').value = keyContent;
  document.getElementById('key-content-section').style.display = 'block';
  document.getElementById('reveal-key-btn').style.display = 'none';
});

ipcRenderer.on('notify-export-private-key-success', (event, filePath) => {
  alert($.i18n('app-export-key-success-message', filePath));
  
  const openFolder = confirm($.i18n('app-export-key-open-folder-confirm'));
  if (openFolder) {
    shell.showItemInFolder(filePath);
  }
});

ipcRenderer.on('notify-export-private-key-error', (event, errMessage) => {
  alert($.i18n('app-export-key-error-generic', errMessage));
});

// Helper function to check if password is strong
function isStrongPassword(password) {
  if (password.length < 12) return false;
  
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[^a-zA-Z0-9]/.test(password); // any non-alphanumeric character
  
  return hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar;
}

// Helper function to show modal error
function showModalError(message) {
  const errorDiv = document.getElementById('modal-error-message');
  const errorText = document.getElementById('modal-error-text');
  errorText.innerHTML = message;
  errorDiv.style.display = 'block';
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
  document.getElementById('key-content-textarea').value = '';
  document.getElementById('export-password').value = '';
  document.getElementById('export-password-confirm').value = '';
  if (clipboardTimeout) {
    clearTimeout(clipboardTimeout);
    clipboard.clear();
  }
});