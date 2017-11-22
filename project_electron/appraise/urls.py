from django.conf.urls import url
from appraise.views import AppraiseView, AppraisalNoteUpdateView, AppraiseTransferView

urlpatterns = [

    url(r'^$', 	AppraiseView.as_view(), name='appraise-main'),
    url(r'^(?P<pk>\d+)/note/$', AppraisalNoteUpdateView.as_view(), name='appraise-note'),
    url(r'^(?P<pk>\d+)/accept/$', AppraiseTransferView.as_view(action=70), name='accept-transfer'),
    url(r'^(?P<pk>\d+)/reject/$', AppraiseTransferView.as_view(action=60), name='reject-transfer'),

]
