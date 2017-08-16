from django.conf.urls import url
from transfer_app.views import MainView
from orgs.views import OrganizationListView

urlpatterns = [
    url(r'^$', 	MainView.as_view(), name='app_home'),
    url(r'^org/list/$', 	OrganizationListView.as_view(), name='org_list'),
]
