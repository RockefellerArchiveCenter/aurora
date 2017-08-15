from django.conf.urls import url
from transfer_app.views import MainView

urlpatterns = [
    url(r'^$', 	MainView.as_view()),
]
