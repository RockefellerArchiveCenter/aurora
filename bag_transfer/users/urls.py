from bag_transfer.users.views import (UserPasswordChangeView, UsersCreateView,
                                      UsersDetailView, UsersEditView,
                                      UsersListView)
from django.conf.urls import url

app_name = "users"

urlpatterns = [
    url(r"^$", UsersListView.as_view(), name="list"),
    url(r"^(?P<pk>\d+)/$", UsersDetailView.as_view(), name="detail"),
    url(r"^add/$", UsersCreateView.as_view(), name="add"),
    url(r"^(?P<pk>\d+)/edit/$", UsersEditView.as_view(), name="edit"),
    url(
        r"^change-password/$", UserPasswordChangeView.as_view(), name="password-change"
    ),
]
