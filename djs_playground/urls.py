from django.conf import settings
from django.urls import re_path, include
from django.conf.urls.static import static
from django.contrib import admin
from djs_playground.views import index

urlpatterns = [
    re_path(r'^$', index, name='index'),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^summernote/', include('django_summernote.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
