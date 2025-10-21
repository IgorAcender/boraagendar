from django.urls import path

from scheduling.views import public as public_views

app_name = "public"

urlpatterns = [
    path("agendar/<slug:tenant_slug>/", public_views.booking_start, name="booking_start"),
    path(
        "agendar/<slug:tenant_slug>/confirmar/",
        public_views.booking_confirm,
        name="booking_confirm",
    ),
    path(
        "agendar/<slug:tenant_slug>/sucesso/",
        public_views.booking_success,
        name="booking_success",
    ),
]
