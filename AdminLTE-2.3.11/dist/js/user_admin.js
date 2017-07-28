$(document).ready(function(){
  var user_admin = [["Message1", "Message1","Message1","Message1"],["Message2","Message2","Message2","Message2"]]
  var log_messages = [[],[]]

  $('#user-admin-table').DataTable({
    data: user_admin,
    columns: [
      {title: "Column 1"},
      {title: "Column 2"},
      {title: "Column 3"},
      {title: "Column 4"}    
    ]
  });
});
