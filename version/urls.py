from django.conf.urls import url,include
from . import views

from django.conf import settings
import django.contrib.auth.views


urlpatterns = [
    url(r'^new/(\d+)/$', views.new_version, name='new_version'),
    url(r'^reconcile/(\d+)/$', views.reconcile, name='reconcile'),
    url(r'^edit/(\d+)/$', views.edit, name='edit'),
    url(r'^docx/(\d+)/$', views.docx, name='docx'),
    url(r'^pdf/(\d+)/$', views.pdf, name='pdf'),
    url(r'^odt/(\d+)/$', views.odt, name='odt'),
    url(r'^upload/(\d+)?/$', views.upload, name='upload'),
    url(r'^details/(\d+)/$', views.details, name='details'),
    url(r'^delete/(\d+)/$', views.delete, name='delete'),
    url(r'^save/$', views.save, name='save'),
    url(r'^tree/(\d+)?/$', views.vtree, name='vtree'),
    url(r'^list/(\d+)?/$', views.vlist, name='vlist'),
]


