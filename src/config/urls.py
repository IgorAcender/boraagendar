from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve as static_serve
from scheduling.urls import whatsapp as whatsapp_urls
from config.spa import serve_spa

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", lambda request: HttpResponse("ok"), name="healthz"),
    path("api/", include("config.urls_api")),
    # ⭐ Explicit static files serving (BEFORE SPA routes to prevent catchall interference)
    re_path(r'^static/(?P<path>.+)$', static_serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    path("dashboard/", include("scheduling.urls.dashboard")),
    path("dashboard/whatsapp/", include(whatsapp_urls)),
    path("accounts/", include("accounts.urls")),
    
    # ⭐ React SPA Routes - ANTES DO CATCHALL (mais específico primeiro)
    re_path(r'^app(?:/.*)?$', serve_spa, {'path': 'index.html'}, name='spa-app'),
    re_path(r'^financeiro/.*$', serve_spa, {'path': 'index.html'}, name='spa-financeiro'),
    re_path(r'^transacoes.*$', serve_spa, {'path': 'index.html'}, name='spa-transacoes'),
    re_path(r'^relatorios.*$', serve_spa, {'path': 'index.html'}, name='spa-relatorios'),
    re_path(r'^configuracoes.*$', serve_spa, {'path': 'index.html'}, name='spa-configuracoes'),
    
    # Django public URLs (mais geral, vai por último)
    path("", include("scheduling.urls.public")),
    path("", RedirectView.as_view(pattern_name="dashboard:index", permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
