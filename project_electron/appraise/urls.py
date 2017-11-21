from django.conf.urls import url
from appraise.views import AppraiseView, AppraisalNoteUpdateView

urlpatterns = [

    url(r'^$', 	AppraiseView.as_view(), name='appraise-main'),
    url(r'^(?P<pk>\d+)/note/$', AppraisalNoteUpdateView.as_view(), name='appraise-note'),

]
