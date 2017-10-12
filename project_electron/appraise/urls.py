from django.conf.urls import url
from appraise.views import AppraiseView

urlpatterns = [

    url(r'^appraise/', 	AppraiseView.as_view(), name='appraise-main'),
    
]
