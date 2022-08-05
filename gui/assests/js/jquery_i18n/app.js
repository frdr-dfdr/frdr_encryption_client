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
          + '<a id="open-frdr-profile" href="#">' + $.i18n('app-request-access-profile') +'</a>'
          + $.i18n('app-request-access-intro2'));

      $('#open-frdr-profile').on("click", function(){
        openFRDRProfile();
      });

      // Add hyperlink to open FRDR Deposit Dashboard
      $('#frdr-dashboard-link').html('<a id="open-frdr-dashboard" href="#">' + $.i18n('app-encrypt-done-text2') +'</a>');

      $('#open-frdr-dashboard').on("click", function(){
        openFRDRDepositDashboard();
      });

      // tooltip
      $('#login-url-tooltip').attr("data-original-title", $.i18n('app-login-url-tooltip'));

      $('#copy_to_clipboard').attr("data-original-title", $.i18n('app-profile-copy-to-clipboard'));

      $("#send_to_frdr").parent().attr("data-original-title", $.i18n("app-profile-send-to-frdr-disabled"));
      
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
  
