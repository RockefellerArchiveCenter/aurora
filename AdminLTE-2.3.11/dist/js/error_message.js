$(document).ready(function(){
  var error_messages = [["Message", "Message","Message"],["Message","Message","Message"]]
  var log_messages = [[],[]]

  $('#error-messages-table').DataTable({
    data: error_messages,
    columns: [
      {title: "Time"},
      {title: "Summary"},
      {title: "Result"}
    ]
  });
});
