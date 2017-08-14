$(document).ready( function () {
  var dataset = [["Transfer File One","Complete","Date-Time","None"],["Transfer File Two","Complete","Date-Time","None"]]

  $('#transfer-log-table').DataTable({
    data: dataset,
    columns: [
      {title: "Transfer File Name"},
      {title: "Transfer Status"},
      {title: "Date/Time"},
      {title: "Action Items"}
    ]
  });
} );
