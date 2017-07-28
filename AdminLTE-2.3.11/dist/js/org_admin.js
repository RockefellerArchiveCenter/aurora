$(document).ready(function(){
  var org_admin = [["Message1", "Message1","Message1","Message1","Message1"],["Message2","Message2","Message2","Message2","Message2"]]
  var log_messages = [[],[]]

  $('#org-admin-table').DataTable({
    data: org_admin,
    columns: [
      {title: "Column 1"},
      {title: "Column 2"},
      {title: "Column 3"},
      {title: "Column 4"},
      {title: "Column 5"}
    ]
  });
});
