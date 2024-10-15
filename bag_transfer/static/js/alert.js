var global_fadein_time = 300;

$(document).ready(function(){
});

function displayMessage(color, message) {
  var iconClass = 'check_circle_outline';
  if (color === 'orange') {
    iconClass = 'error_outline';
  }

  $('#messages').empty().append(
    '<div class="alert alert--'+color+' alert-dismissible">\
      <button class="alert__button" aria-label="Close" data-dismiss="alert">\
        <span class="material-icon" aria-hidden="true">close</span>\
      </button>\
      <div class="alert__icon-wrapper">\
        <span class="alert__icon" aria-hidden="true">'+iconClass+'</span>\
      </div>\
      <div class="alert__text-wrapper">\
        <p class="alert__text">'+message+'</p>\
      </div>\
    </div>').fadeIn(global_fadein_time);
}
