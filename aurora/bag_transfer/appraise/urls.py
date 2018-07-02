from django.conf.urls import url
from bag_transfer.appraise.views import AppraiseView

urlpatterns = [
    url(r'^$', 	AppraiseView.as_view(), name='list'),
]
