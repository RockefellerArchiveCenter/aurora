var global_fadeout_time = 1300;
var global_fadein_time = 300;


$(document).ready(function(){
    dismiss_messages();
});

function displayMessage(type, message, dismissible) {
  console.log(dismissible)
  var iconClass = 'check_circle_outline'
  if (type == 'orange') {
    iconClass = 'error_outline'
  }
  $('#messages').empty()
  if (dismissible) {
    $('#messages').append(
      '<div class="alert alert-'+type+' alert-dismissible">\
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
  } else {
    $('#messages').append(
      '<div class="alert alert--'+type+'">\
        <div class="alert__icon-wrapper">\
          <span class="alert__icon" aria-hidden="true">'+iconClass+'</span>\
        </div>\
        <div class="alert__text-wrapper">\
          <p class="alert__text">'+message+'</p>\
        </div>\
      </div>').fadeIn(global_fadein_time);
  }
  setTimeout(function(){
    $('.alert-dismissible').fadeOut(global_fadeout_time).remove();
  }, 2000);
}

function dismiss_messages() {
	var ele = $('.alert-dismissible');

	if(ele.length){
		setTimeout(function(){
			$('.alert-dismissible').fadeOut(global_fadeout_time);
		}, 2000);

	}
}
