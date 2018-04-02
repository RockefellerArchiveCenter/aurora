var confirm_modal = $('#modal-warning');
var last_active_rs = 0;
$(function () {
  $('.object-delete-button').click(function(e){
  	e.preventDefault();
    object_type = $(this).data('object')
  	last_active_rs = $(this).closest('tr').attr('rel');
  	confirm_modal.find('.object-api-url').attr('href', $(this).attr('href'));
    confirm_modal.find('.modal-title').html('Delete ' + object_type.replace(/\-/g, ' ') + '?')
  	confirm_modal.modal('show');
  });

  $('.object-modal-delete-button').click(function(e){
  	$.get(confirm_modal.find('.object-api-url').attr('href'),{},function(resp){
  		if(resp.success){
        var table = '.' + object_type + '-table'
  			var len_rows = $(table + ' tbody tr').length;
  			$(table + ' tr[rel="' + last_active_rs + '"]').fadeOut().remove();
  			if (len_rows <= 1){
  				$(table).fadeOut().remove();

  				$('.has-no-' + object_type + '-p').closest('.box-body').removeClass('no-padding');
  				$('.has-no-' + object_type + '-p').show()
          $('.'+object_type+'-add').fadeIn();
  			}
  		} else {
  			alert('Sorry there was a problem deleting the ' + object_type.replace(/\-/g, ' ') + '.');
  		}
  	});
  	confirm_modal.modal('hide');
  });
});
