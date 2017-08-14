# Project Electron Transfer User Interfaces

This directory contains the UIs for users from donor/depositor organizations to track transfers, view error messages, and manage user accounts. The UIs were created using templates from [AdminLTE](https://adminlte.io/) and Bootstrap 3.

## Transfer Log
The [Transfer Log](AdminLTE-2.3.11/transfer_log.html)  is the primary interface to track information about transfers. Enables the user to view the transfer file names, size, transfer status, date/time, and associated notifications related to the transfer.

## Detail View
The [Detail View](AdminLTE-2.3.11/detail_view.html) provides more information about a specific transfer. It is accessible by links from the Transfer Log, and displays the metadata, a table of error messages, and log displaying notifications.

## Error Message
The [Error Message](AdminLTE-2.3.11/error_message) gives details on any errors that occurred during transfer, for example, if a bag has an invalid filename, a virus is found, or the required metadata elements are not present. This view is accessible via links from the Transfer Log and the Detail View.

## User Admin
The [User Admin](AdminLTE-2.3.11/user_admin) enables the administrative management of an organization's user information. It includes the ability to add or delete users, edit and view user information, and add a user to an organization.

## Organization Admin
The [Organization Admin](AdminLTE-2.3.11/org_admin) enables administrative management of donor organizations by the Rockefeller Archive Center. It provides a table with information on organization name and descriptive information.
