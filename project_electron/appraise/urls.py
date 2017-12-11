from django.conf.urls import url
from appraise.views import AppraiseView, AppraisalNoteUpdateView

urlpatterns = [

    url(r'^$', 	AppraiseView.as_view(), name='appraise-main'),
]