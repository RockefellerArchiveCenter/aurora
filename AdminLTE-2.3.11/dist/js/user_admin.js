$(document).ready(function(){
  var user_admin = [["Message1", "Message1","Message1"],["Message2","Message2","Message2"]]
  var log_messages = [[],[]]

  $('#user-admin-table').DataTable({
    data: user_admin,
    columns: [
      {title: "First Name"},
      {title: "Last Name"},
      {title: "Email"}
    ]
  });
});
