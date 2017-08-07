$(document).ready(function(){
  var error_messages = [["Message", "Message","Message"],["Message","Message","Message"]]

  $('#error-messages-table').DataTable({
    data: error_messages,
    columns: [
      {title: "Date/Time"},
      {title: "Summary"},
      {title: "Result"}
    ]
  });
});
