"""Aurora URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include('blog.urls'))
"""
from asterism.views import PingView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, re_path

from bag_transfer.transfers.views import DashboardView
from bag_transfer.users.views import (SplashView,
                                      UserPasswordResetCompleteView,
                                      UserPasswordResetConfirmView,
                                      UserPasswordResetDoneView,
                                      UserPasswordResetView)

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^app/$", DashboardView.as_view(), name="app_home"),
    re_path(
        r"^app/transfers/",
        include("bag_transfer.transfers.urls", namespace="transfers"),
    ),
    re_path(r"^app/orgs/", include("bag_transfer.orgs.urls", namespace="orgs")),
    re_path(r"^app/bagit-profiles/", include("bag_transfer.bagit_profiles.urls", namespace="bagit-profiles")),
    re_path(r"^app/users/", include("bag_transfer.users.urls", namespace="users")),
    re_path(
        r"^reset-password/$",
        UserPasswordResetView.as_view(
            email_template_name="users/password_reset_email.html",
            subject_template_name="users/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    re_path(
        r"^reset-password/done/$",
        UserPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    re_path(
        r"^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,40})/$",
        UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    re_path(
        r"^reset/done/$",
        UserPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    re_path(
        r"^app/accession/",
        include("bag_transfer.accession.urls", namespace="accession"),
    ),
    re_path(r"^app/appraise/", include("bag_transfer.appraise.urls", namespace="appraise")),
    re_path(r"^app/rights/", include("bag_transfer.rights.urls", namespace="rights")),
    re_path(r"^$", SplashView.as_view(), name="splash"),
    re_path(
        r"^login/$",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    re_path(r"^logout/$", auth_views.LogoutView.as_view(next_page="/login"), name="logout"),
    re_path(r"^api/", include("bag_transfer.api.urls")),
    re_path(r'^status/', PingView.as_view(), name="ping"),
]
