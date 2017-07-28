$(document).ready( function () {
  var dataset = [["File One","Complete","01/02/03","None"],["File Two","Complete","02/03/04","None"]]
  
  $('#list-view-table').DataTable({
    data: dataset,
    columns: [
      {title: "File Name"},
      {title: "Transfer Status"},
      {title: "Date"},
      {title: "Action Items"}
    ]
  });
} );
