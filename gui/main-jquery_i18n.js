jQuery(document).ready(function() {
    
  $.i18n().load({
    en: '../languages/en.json',
    fr: '../languages/fr.json'
  }).done( function() { console.log('done!') } );
    
  var update_texts = function() {
    // if (localStorage.getItem("locale") != null) {
    //   $.i18n().locale = localStorage.getItem("locale");
    // }
    $('body').i18n();
    $('#account-dropdown').html($.i18n('app-navbar-account') + '<span class="caret"></span>');
    $('#depositor-dropdown').html($.i18n('app-navbar-depositor') + '<span class="caret"></span>');
    $('#requester-dropdown').html($.i18n('app-navbar-requester') + '<span class="caret"></span>');
    $('#locale-dropdown').html($.i18n('app-navbar-locale') + '<span class="caret"></span>');
  };

  update_texts();

  $('.lang-switch').click(function(e) {
    e.preventDefault();
    $.i18n().locale = $(this).data('locale');
    // localStorage.setItem("locale", $.i18n().locale);
    update_texts();
  });

  var localeCode = {
    "English": "EN", 
    "Français": "FR"
  };
  $('#locale-menu li').click(function(){
    $('#locale').html(localeCode[$(this).text()] + '<span class="caret"></span>')
  });

});

