from django.conf.urls import url,include
from . import views

from django.conf import settings
import django.contrib.auth.views
from django.urls import path

from jwt_auth import views as jwt_auth_views


urlpatterns = [
    url(r'^$', views.frontend, name='frontend'),
    url(r'^new/(\d+)/$', views.new_version_restricted.as_view(), name='new_version'),
    url(r'^conflicts/(\d+)/$', views.conflicts_restricted.as_view(), name='conflicts'),
    url(r'^rebase/$', views.rebase_restricted.as_view(), name='rebase'),
    url(r'^merge/(\d+)/$', views.merge_restricted.as_view(), name='merge'),
    url(r'^mergereq/(\d+)/$', views.merge_request_restricted.as_view(), name='merge_request'),
    url(r'^mergereset/(\d+)/$', views.reset_merge_request_restricted.as_view(), name='merge_reset'),
    #url(r'^edit/(\d+)/$', views.edit, name='edit'),
    url(r'^docx/(\d+)/$', views.docx, name='docx'),
    url(r'^pdf/(\d+)/$', views.pdf, name='pdf'),
    url(r'^odt/(\d+)/$', views.odt_restricted.as_view(), name='odt'),
    url(r'^upload/(\d+)?/$', views.upload_restricted.as_view(), name='upload'),
    url(r'^details/(\d+)/$', views.details_restricted.as_view(), name='details'),
    url(r'^delete/(\d+)/$', views.delete_restricted.as_view(), name='delete'),
    url(r'^save/$', views.save_restricted.as_view(), name='save'),
    url(r'^tree/(\d+)?/$', views.vtree_restricted.as_view(), name='vtree'),
    url(r'^list/(\d+)?/$', views.vlist_restricted.as_view(), name='vlist'),
    path("token-auth/", jwt_auth_views.jwt_token),
    path("token-refresh/", jwt_auth_views.refresh_jwt_token)
    #url(r'^check/(\d+)/$', views.checkAndMerge, name='checkVersion'),
]


