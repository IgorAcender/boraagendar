from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("config.urls_api")),
    path("", include("scheduling.urls.public")),
    path("dashboard/", include("scheduling.urls.dashboard")),
    path("accounts/", include("accounts.urls")),
    path("", RedirectView.as_view(pattern_name="dashboard:index", permanent=False)),
]
