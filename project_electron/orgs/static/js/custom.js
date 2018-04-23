var global_fadeout_time = 1300;


$(document).ready(function(){
    dismiss_messages();

});

var dismiss_messages = function(){
	var ele = $('.alert-dismissible');

	if(ele.length){
		setTimeout(function(){
			$('.alert-dismissible').fadeOut(global_fadeout_time);
		}, 2000);

	}
}
