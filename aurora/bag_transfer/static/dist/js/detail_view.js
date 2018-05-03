$(document).ready(function(){
  var error_messages = [["Message1", "Message1","Message1"],["Message2","Message2","Message2"]]

  var log_messages = [["Message1", "Message1"],["Message2", "Message2"]]

  $('#error-messages-table').DataTable({
    data: error_messages,
    columns: [
      {title: "Date/Time"},
      {title: "Summary"},
      {title: "Result"}
    ]
  });

  $('#log-table').DataTable({
      data: log_messages,
      columns: [
          {title: "Date/Time"},
          {title: "Message"}
      ]
  });
});
