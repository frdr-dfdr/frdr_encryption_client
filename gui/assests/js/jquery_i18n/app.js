$.i18n.debug = true;

var update_texts = function() {
  var i18n = $.i18n();
  console.log(i18n.locale);
  if (localStorage.getItem("locale") != null) {
    i18n.locale = localStorage.getItem("locale");
  }
  i18n.load('../languages/' + i18n.locale + '.json', i18n.locale).done(
    function () {
      $('body').i18n();
      // navbar
      $('#account-dropdown').html($.i18n('app-navbar-account') + '<span class="caret"></span>');
      $('#depositor-dropdown').html($.i18n('app-navbar-depositor') + '<span class="caret"></span>');
      $('#requester-dropdown').html($.i18n('app-navbar-requester') + '<span class="caret"></span>');
      $('#locale-dropdown').html($.i18n('app-navbar-locale') + '<span class="caret"></span>');

      // tooltip
      $('#login-url-tooltip').attr("data-original-title", $.i18n('app-login-url-tooltip'));

      $('#encrypt-input-tooltip').attr("data-original-title", $.i18n('app-depositor-encrypt-input-tooltip'));
      $('#encrypt-output-tooltip').attr("data-original-title", $.i18n('app-depositor-encrypt-output-tooltip'));

      $('#dataset-tooltip').attr("data-original-title", $.i18n('app-depositor-grant-access-dataset-tooltip'));
      $('#requester-tooltip').attr("data-original-title", $.i18n('app-depositor-grant-access-requester-tooltip'));
      $('#expire-tooltip').attr("data-original-title", $.i18n('app-depositor-grant-access-expire-tooltip'));

      $('#decrypt-url-tooltip').attr("data-original-title", $.i18n('app-requester-decrypt-url-tooltip'));
      $('#decrypt-input-tooltip').attr("data-original-title", $.i18n('app-requester-decrypt-input-tooltip'));
      $('#decrypt-output-tooltip').attr("data-original-title", $.i18n('app-requester-decrypt-output-tooltip'));
      
      $('[data-toggle="tooltip"]').tooltip();
    }
  );  
};

$( document ).ready( function ( $ ) {
  update_texts();
} );

$('.lang-switch').click(function(e) {
    e.preventDefault();
    $.i18n().locale = $(this).data('locale');
    localStorage.setItem("locale", $.i18n().locale);
    update_texts();

  });
  
