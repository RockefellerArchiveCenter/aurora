$(document).ready( function () {
  var dataset = [["Transfer File One","Complete","Date-Time", "File Size", "None"],["Transfer File Two","Complete","Date-Time", "File Size", "None"]]

  $('#transfer-log-table').DataTable({
    data: dataset,
    columns: [
      {title: "Transfer File Name"},
      {title: "Transfer Status"},
      {title: "Date/Time"},
      {title: "Size"},
      {title: "Action Items"}
    ]
  });
} );
