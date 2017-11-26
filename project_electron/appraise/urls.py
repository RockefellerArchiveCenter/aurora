from django.conf.urls import url
from appraise.views import AppraiseView, AppraisalNoteUpdateView, AcceptTransferView, RejectTransferView

urlpatterns = [

    url(r'^$', 	AppraiseView.as_view(), name='appraise-main'),
    url(r'^(?P<pk>\d+)/note/$', AppraisalNoteUpdateView.as_view(), name='appraise-note'),
    url(r'^(?P<pk>\d+)/accept/$', AcceptTransferView.as_view(), name='appraise-accept'),
    url(r'^(?P<pk>\d+)/reject/$', RejectTransferView.as_view(), name='appraise-reject'),

]
