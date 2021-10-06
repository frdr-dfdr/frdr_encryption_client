const {ipcRenderer} = require('electron');

ipcRenderer.send("get-entity-id");

ipcRenderer.on('notify-get-entity-id-done', function (event, result) {
  document.getElementById("vault_user_id").innerHTML = result;
});

ipcRenderer.on('notify-get-entity-id-error', function (event, errMessage) {
  alert($.i18n('app-get-entity-id-error', errMessage), "");
});

ipcRenderer.on('notify-get-entity-name-done', function (event, result) {
  document.getElementById("vault_email").innerHTML = result;
});

ipcRenderer.on('notify-get-entity-name-error', function (event, errMessage) {
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
        $("#copy_to_clipboard").removeClass("glyphicon-file").addClass("glyphicon-ok");
        setTimeout(function(){ 
          $("#copy_to_clipboard").removeClass("glyphicon-ok").addClass("glyphicon-file"); 
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

$(document).ready(function() {
  $('[data-toggle="tooltip"]').tooltip({
    container: 'body'
  });
  
  $('.js-copy').click(function() {
    var text = $("#vault_user_id").html();
    var el = $(this);
    copyToClipboard(text, el);
  });
});