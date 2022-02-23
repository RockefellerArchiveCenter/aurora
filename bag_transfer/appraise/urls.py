from django.urls import re_path

from bag_transfer.appraise.views import AppraiseDataTableView, AppraiseView

app_name = 'appraise'

urlpatterns = [
    re_path(r"^$", AppraiseView.as_view(), name="list"),
    re_path(r"^datatable/$", AppraiseDataTableView.as_view(), name="datatable"),
]
