# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect

# Fix "View Site" button in Django admin panel
admin.site.site_url = "http://localhost:3000"


def redirect_to_frontend(request):
    """Redirect root URL to the React frontend login page."""
    return HttpResponseRedirect("http://localhost:3000/login")


urlpatterns = [
    path("",       redirect_to_frontend),
    path("admin/", admin.site.urls),
    path("api/",   include("greentrace.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    