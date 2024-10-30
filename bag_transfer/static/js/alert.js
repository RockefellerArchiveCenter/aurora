var global_fade_time = 300;

$(document).ready(function() {
  // Enable closing of all alert messages
  $('#messages').on('click', '.alert__button', function() {
    $(this).closest('.alert').fadeOut(global_fade_time, function() {
      $(this).remove();
    });
  });
});

function displayMessage(color, message) {
  var iconClass = 'check_circle_outline';
  if (color === 'orange') {
    iconClass = 'error_outline';
  }

  $('#messages').empty().append(
    '<div class="alert alert--'+color+'">\
      <button type="button" class="alert__button" aria-label="Close alert message">\
        <span class="material-icon" aria-hidden="true">close</span>\
      </button>\
      <div class="alert__icon-wrapper">\
        <span class="alert__icon" aria-hidden="true">'+iconClass+'</span>\
      </div>\
      <div class="alert__text-wrapper">\
        <p class="alert__text">'+message+'</p>\
      </div>\
    </div>').fadeIn(global_fade_time);
}
