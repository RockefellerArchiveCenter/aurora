$(document).ready( function () {
  var dataset = [["File One","Complete","Date-Time","None"],["File Two","Complete","Date-Time","None"]]

  $('#list-view-table').DataTable({
    data: dataset,
    columns: [
      {title: "File Name"},
      {title: "Transfer Status"},
      {title: "Date/Time"},
      {title: "Action Items"}
    ]
  });
} );
