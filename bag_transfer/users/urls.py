from django.urls import re_path

from bag_transfer.users.views import (UserPasswordChangeView, UsersCreateView,
                                      UsersDetailView, UsersEditView,
                                      UsersListView)

app_name = "users"

urlpatterns = [
    re_path(r"^$", UsersListView.as_view(), name="list"),
    re_path(r"^(?P<pk>\d+)/$", UsersDetailView.as_view(), name="detail"),
    re_path(r"^add/$", UsersCreateView.as_view(), name="add"),
    re_path(r"^(?P<pk>\d+)/edit/$", UsersEditView.as_view(), name="edit"),
    re_path(
        r"^change-password/$", UserPasswordChangeView.as_view(), name="password-change"
    ),
]
