from django.conf.urls import url,include
from . import views

from django.conf import settings
import django.contrib.auth.views

urlpatterns = [
    url(r'^new/(\d+)/$', views.new_version, name='new_version'),
    url(r'^reconcile/(\d+)/$', views.reconcile, name='reconcile'),
    url(r'^edit/(\d+)/$', views.edit, name='edit'),
    url(r'^save/$', views.save, name='save'),
]
