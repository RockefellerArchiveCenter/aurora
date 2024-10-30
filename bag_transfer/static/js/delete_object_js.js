	var confirm_modal = $('#modal-warning');
	var last_active_rs = 0;

	$(function () {
		$('.object-delete-button').click(function(e){
			e.preventDefault();
			object_type = $(this).data('object')
			last_active_rs = $(this).closest('tr').attr('rel');
			confirm_modal.attr('data-api-url', $(this).attr('href'));
			confirm_modal.find('.modal-title').html('Delete ' + object_type.replace(/\-/g, ' ') + '?')
			console.log("Opening modal for deleting: ", object_type);
			MicroModal.show("modal-warning");
		});

		$('.object-modal-delete-button').click(function(e){
			$.get(confirm_modal.attr('data-api-url'),{},function(resp){
				if(resp.success){
					let table = '.' + object_type + '-table'
					let len_rows = $(table + ' tbody tr').length;

					console.log("Rows before deletion:", len_rows);
					$(table + ' tr[rel="' + last_active_rs + '"]').fadeOut().remove(); //delete row
					let titleElement = $('#' + object_type + '-title');
					titleElement.focus(); //move focus to h2 after row is removed

					if (len_rows <= 1){
						$(table).remove();

						// Create the "has-no-" paragraph with object_type
						let paragraphText = object_type === 'bagit-profile' ? 'There is no existing BagIt profile.' : 'There are no existing rights statements.';
						let paragraph = $('<p class="has-no-' + object_type + '-p">' + paragraphText + '</p>');

						titleElement.parent().after(paragraph);
						paragraph.show();
					}
				} else {
					alert('Sorry there was a problem deleting the ' + object_type.replace(/\-/g, ' ') + '.');
				}
			});
			MicroModal.close("modal-warning");
		});
	});
