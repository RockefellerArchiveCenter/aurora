$(document).ready(function(){
  var org_admin = [["Message1", "Message1","Message1","Message1"],["Message2","Message2","Message2","Message2"]]
  var log_messages = [[],[]]

  $('#org-admin-table').DataTable({
    data: org_admin,
    columns: [
      {title: "First Name"},
      {title: "Last Name"},
      {title: "Email"},
      {title: "Organization"}
    ]
  });
});
