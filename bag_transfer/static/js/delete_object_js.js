var confirm_modal = $('#modal-warning');
var last_active_rs = 0;
$(function () {
  $('.object-delete-button').click(function(e){
  	e.preventDefault();
    object_type = $(this).data('object')
  	last_active_rs = $(this).closest('tr').attr('rel');
  	confirm_modal.attr('data-api-url', $(this).attr('href'));
    confirm_modal.find('.modal-title').html('Delete ' + object_type.replace(/\-/g, ' ') + '?')
  	MicroModal.show("modal-warning");
  });

  $('.object-modal-delete-button').click(function(e){
  	$.get(confirm_modal.attr('data-api-url'),{},function(resp){
  		if(resp.success){
        var table = '.' + object_type + '-table'
  			var len_rows = $(table + ' tbody tr').length;
  			$(table + ' tr[rel="' + last_active_rs + '"]').fadeOut().remove();
  			if (len_rows <= 1){
  				$(table).fadeOut().remove();
  				$('.has-no-' + object_type + '-p').show()
  			}
  		} else {
  			alert('Sorry there was a problem deleting the ' + object_type.replace(/\-/g, ' ') + '.');
  		}
  	});
  	MicroModal.close("modal-warning");
  });
});
