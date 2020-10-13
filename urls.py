from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve
from django.conf import settings


def protected_serve(request, path, document_root=None, show_indexes=True):
    return serve(request, path, settings.STATIC_ROOT, show_indexes)

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^version/', include('barney_version.urls')),
]

