const {ipcRenderer} = require('electron');

// Allow the user to logout
document.getElementById("logout").addEventListener("click", logout);

function logout() {
  // document.location.href = "https://auth.globus.org/v2/web/logout"
  ipcRenderer.send("logout");
}

ipcRenderer.on('notify-logout-done', function (event) {
  ipcRenderer.send("unauthenticated");
});

ipcRenderer.on('notify-logout-error', function (event, errMessage) {
  alert(`Error logging out. ${errMessage}`, "")
});