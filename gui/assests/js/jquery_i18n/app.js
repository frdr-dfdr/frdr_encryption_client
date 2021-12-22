$.i18n.debug = true;

var update_texts = function() {
  var i18n = $.i18n();
  if (localStorage.getItem("locale") != null) {
    i18n.locale = localStorage.getItem("locale");
  }
  i18n.load('../languages/' + i18n.locale + '.json', i18n.locale).done(
    function () {
      $('body').i18n();
      // navbar
      $('#account-dropdown').html($.i18n('app-navbar-account') + '<span class="caret"></span>');
      $('#locale-dropdown').html($.i18n('app-navbar-locale') + '<span class="caret"></span>');

      // Add hyperlink to open FRDR profile page on request access page
      $('#vault-id-intro').html($.i18n('app-request-access-intro1') 
          + '<a id="open-frdr-profile">' + $.i18n('app-request-access-profile') +'</a>'
          + $.i18n('app-request-access-intro2'));

      $('#open-frdr-profile').on("click", function(){
        openFRDRProfile();
      });

      // tooltip
      $('#login-url-tooltip').attr("data-original-title", $.i18n('app-login-url-tooltip'));

      $('#encrypt-input-tooltip').attr("data-original-title", $.i18n('app-encrypt-input-tooltip'));
      $('#encrypt-output-tooltip').attr("data-original-title", $.i18n('app-encrypt-output-tooltip'));

      $('#dataset-tooltip').attr("data-original-title", $.i18n('app-grant-access-dataset-tooltip'));
      $('#requester-tooltip').attr("data-original-title", $.i18n('app-grant-access-requester-tooltip'));
      $('#expire-tooltip').attr("data-original-title", $.i18n('app-grant-access-expire-tooltip'));

      $('#decrypt-url-tooltip').attr("data-original-title", $.i18n('app-decrypt-url-tooltip'));
      $('#decrypt-input-tooltip').attr("data-original-title", $.i18n('app-decrypt-input-tooltip'));
      $('#decrypt-output-tooltip').attr("data-original-title", $.i18n('app-decrypt-output-tooltip'));

      $('#copy_to_clipboard').attr("data-original-title", $.i18n('app-profile-copy-to-clipboard'));
      
      
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
  
