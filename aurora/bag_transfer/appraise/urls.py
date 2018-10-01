from django.conf.urls import url
from bag_transfer.appraise.views import AppraiseView, AppraiseDataTableView

urlpatterns = [
    url(r'^$', 	AppraiseView.as_view(), name='list'),
    url(r'^datatable/$', AppraiseDataTableView.as_view(), name='datatable'),
]
