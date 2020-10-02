from django.conf.urls import url,include
from . import views

from django.conf import settings
import django.contrib.auth.views
from django.urls import path

from jwt_auth import views as jwt_auth_views


urlpatterns = [
    url(r'^new/(\d+)/$', views.new_version, name='new_version'),
    url(r'^conflicts/(\d+)/$', views.conflicts, name='conflicts'),
    url(r'^merge/(\d+)/$', views.merge, name='merge'),
    #url(r'^edit/(\d+)/$', views.edit, name='edit'),
    url(r'^docx/(\d+)/$', views.docx, name='docx'),
    url(r'^pdf/(\d+)/$', views.pdf, name='pdf'),
    url(r'^odt/(\d+)/$', views.odt, name='odt'),
    url(r'^upload/(\d+)?/$', views.upload, name='upload'),
    url(r'^details/(\d+)/$', views.details, name='details'),
    url(r'^delete/(\d+)/$', views.delete, name='delete'),
    url(r'^save/$', views.save, name='save'),
    url(r'^tree/(\d+)?/$', views.vtree, name='vtree'),
    url(r'^list/(\d+)?/$', views.vlist, name='vlist'),
    path("token-auth/", jwt_auth_views.jwt_token),
    path("token-refresh/", jwt_auth_views.refresh_jwt_token),
    path("protected-url/", views.RestrictedView.as_view()),
    #url(r'^check/(\d+)/$', views.checkAndMerge, name='checkVersion'),
]


