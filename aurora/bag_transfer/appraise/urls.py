from bag_transfer.appraise.views import AppraiseDataTableView, AppraiseView
from django.conf.urls import url

app_name = 'appraise'

urlpatterns = [
    url(r"^$", AppraiseView.as_view(), name="list"),
    url(r"^datatable/$", AppraiseDataTableView.as_view(), name="datatable"),
]
