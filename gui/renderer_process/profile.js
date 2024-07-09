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

const {ipcRenderer, shell} = require('electron');
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

var profileURL = null;

try {
  var configPath = "";
  if (process.env.NODE_ENV == "development") {
    configPath = path.join(__dirname, '..', '..','config', 'config.yml');
  }
  else {
    var configPath = path.join(__dirname, '..', 'app_gui','config', 'config.yml');
  }
  let fileContents = fs.readFileSync(configPath, 'utf8');
  let config = yaml.load(fileContents);
  profileURL = config["FRDR_PROFILE_URL"];
} catch (e) {
  // log error, the link to FRDR profile page is not working
  console.log(e);
}

ipcRenderer.send("get-entity-id");

ipcRenderer.on('notify-get-entity-id-done', function (_event, result) {
  document.getElementById("vault_user_id").innerHTML = result;
});

ipcRenderer.on('notify-get-entity-id-error', function (_event, errMessage) {
  alert($.i18n('app-get-entity-id-error', errMessage), "");
});

ipcRenderer.on('notify-get-entity-name-done', function (_event, result) {
  document.getElementById("vault_email").innerHTML = result;
});

ipcRenderer.on('notify-get-entity-name-error', function (_event, errMessage) {
  alert($.i18n('app-get-entity-name-error', errMessage), "");
});

function copyToClipboard(text, el) {
  var copyTest = document.queryCommandSupported('copy');
  var elOriginalText = el.attr('data-original-title');
  if (copyTest === true) {
    var copyTextArea = document.createElement("textarea");
    copyTextArea.value = text;
    document.body.appendChild(copyTextArea);
    copyTextArea.select();
    try {
      var successful = document.execCommand('copy');
      var msg = successful ? $.i18n("app-profile-copied") : $.i18n("app-profile-copy-error");
      if (successful) {
        $("#copy_to_clipboard").removeClass("fa-copy").addClass("fa-clipboard-check");
        setTimeout(function(){ 
          $("#copy_to_clipboard").removeClass("fa-clipboard-check").addClass("fa-copy"); 
          el.attr('data-original-title', $.i18n("app-profile-copy-to-clipboard"));
        }, 2000);
      }
      el.attr('data-original-title', msg).tooltip('show');
    } catch (err) {
      console.log('Oops, unable to copy');
    }
    document.body.removeChild(copyTextArea);
    el.attr('data-original-title', elOriginalText);
  } else {
    // Fallback if browser doesn't support .execCommand('copy')
    window.prompt($.i18n("app-profile-copy-error"), text);
  }
}

$('[data-toggle="tooltip"]').tooltip({
  container: 'body'
});

$('.fa-copy').on("click", function() {
  var text = $("#vault_user_id").html();
  var el = $(this);
  copyToClipboard(text, el);
});

function openFRDRProfile() {
  shell.openExternal(profileURL);
}

$('#open-frdr-profile').on("click", function() {
  shell.openExternal(profileURL);
});