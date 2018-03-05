var confirm_modal = $('#modal-warning');
var last_active_rs = 0;
$(function () {
  $('.rights-delete-button').click(function(e){
  	e.preventDefault();
  	last_active_rs = $(this).closest('tr').attr('rel');
  	confirm_modal.find('.rights-statement-api-url').attr('href', $(this).attr('href'));
  	confirm_modal.modal('show');
  });

  $('.rights-modal-delete-button').click(function(e){
  	$.get(confirm_modal.find('.rights-statement-api-url').attr('href'),{},function(resp){
  		if(resp.success){
  			var len_rows = $('.rights-table tbody tr').length;
  			$('.rights-table tr[rel="' + last_active_rs + '"]').fadeOut().remove();
  			if (len_rows <= 1){
  				$('.rights-table').fadeOut().remove();

  				$('.has-no-rights-p').closest('.box-body').removeClass('no-padding');
  				$('.has-no-rights-p').fadeIn();
  			}
  		} else {
  			alert('Sorry there was a problem deleting the rights statement..');
  		}
  	});
  	confirm_modal.modal('hide');
  });
});