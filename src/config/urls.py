from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.generic import RedirectView, TemplateView
from scheduling.urls import whatsapp as whatsapp_urls
from config.spa import serve_spa

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", lambda request: HttpResponse("ok"), name="healthz"),
    path("api/", include("config.urls_api")),
    path("dashboard/", include("scheduling.urls.dashboard")),
    path("dashboard/whatsapp/", include(whatsapp_urls)),
    path("accounts/", include("accounts.urls")),
    path("", include("scheduling.urls.public")),  # Movido para o final (mais específico primeiro)
    
    # ⭐ React SPA Routes - serve index.html para deixar React Router lidar
    re_path(r'^financeiro/.*$', serve_spa, {'path': 'index.html'}, name='spa-financeiro'),
    re_path(r'^agendamentos.*$', serve_spa, {'path': 'index.html'}, name='spa-agendamentos'),
    re_path(r'^relatorios.*$', serve_spa, {'path': 'index.html'}, name='spa-relatorios'),
    re_path(r'^configuracoes.*$', serve_spa, {'path': 'index.html'}, name='spa-configuracoes'),
    re_path(r'^app(?:/.*)?$', serve_spa, {'path': 'index.html'}, name='spa-app'),
    
    path("", RedirectView.as_view(pattern_name="dashboard:index", permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
