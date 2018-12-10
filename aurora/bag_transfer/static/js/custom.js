var global_fadeout_time = 1300;
var global_fadein_time = 300;


$(document).ready(function(){
    dismiss_messages();
});

function displayMessage(type, message, dismissible) {
  console.log(dismissible)
  var iconClass = 'check'
  if (type == 'danger') {
    iconClass = 'times'
  }
  $('#messages').empty()
  if (dismissible) {
    $('#messages').append(
      '<div class="row">\
        <div class="col-md-12">\
          <div class="alert alert-'+type+' alert-dismissible">\
            <button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>\
              <i class="icon fa fa-'+iconClass+'"></i>'+message+'\
          </div>\
        </div>\
      </div>').fadeIn(global_fadein_time);
  } else {
    $('#messages').append(
      '<div class="row">\
        <div class="col-md-12">\
          <div class="alert alert-'+type+'">\
              <i class="icon fa fa-'+iconClass+'"></i>'+message+'\
          </div>\
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
