from django.conf.urls import url
from transfer_app.views import MainView
from orgs.views import OrganizationListView,UsersListView,UsersEditView,UsersCreateView

urlpatterns = [
    url(r'^$', 	MainView.as_view(), name='app_home'),
    url(r'^org/list/$', 	OrganizationListView.as_view(), name='org_list'),

    url(r'^users/$', UsersListView.as_view(), name='users-list'),
    url(r'^users/add/$', UsersCreateView.as_view(), name='users-add'),
    url(r'^users/(?P<pk>\d+)/$', UsersEditView.as_view(), name='users-edit'),
]
