from django.urls import path

from scheduling.views import public as public_views

app_name = "public"

urlpatterns = [
    path("<slug:tenant_slug>/", public_views.tenant_landing, name="tenant_landing"),
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
    path(
        "agendar/<slug:tenant_slug>/api/profissionais/",
        public_views.get_service_professionals,
        name="get_service_professionals",
    ),
    path(
        "agendar/<slug:tenant_slug>/api/horarios/",
        public_views.get_available_slots,
        name="get_available_slots",
    ),
    path(
        "agendar/<slug:tenant_slug>/api/verificar-telefone/",
        public_views.check_phone,
        name="check_phone",
    ),
]
