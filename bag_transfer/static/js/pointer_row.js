// handles mouse and keyboard navigation for table rows.
// Table rows must include data-url and tabindex="0" attributes

$(document).on('keypress click', '.pointer-row', function(e){
  var key = e.which || e.keyCode || 0;
  if (e.type == 'keypress' && key != 13) {
    return false;
  } else {
    window.open($(this).attr('data-url'), '_self')
  }
})
