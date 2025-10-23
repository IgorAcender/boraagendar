from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", lambda request: HttpResponse("ok"), name="healthz"),
    path("api/", include("config.urls_api")),
    path("", include("scheduling.urls.public")),
    path("dashboard/", include("scheduling.urls.dashboard")),
    path("accounts/", include("accounts.urls")),
    path("", RedirectView.as_view(pattern_name="dashboard:index", permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
