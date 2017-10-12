from django.conf.urls import url
from appraise.views import AppraiseView

urlpatterns = [

    url(r'^$', 	AppraiseView.as_view(), name='appraise-main'),

]
