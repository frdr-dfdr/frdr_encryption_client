// Allow the user to logout
document.getElementById("logout").addEventListener("click", logout);

function logout() {
  ipcRenderer.send("logout");
}

ipcRenderer.on('notify-logout-done', function (_event) {
  ipcRenderer.send("unauthenticated");
});

ipcRenderer.on('notify-logout-error', function (_event, errMessage) {
  alert($.i18n('app-logout-error', errMessage), "");
});