from django.urls import include, path
from rest_framework.routers import DefaultRouter

from scheduling.api import viewsets as scheduling_viewsets

router = DefaultRouter()
router.register(r"bookings", scheduling_viewsets.BookingViewSet, basename="booking")
router.register(r"services", scheduling_viewsets.ServiceViewSet, basename="service")
router.register(r"professionals", scheduling_viewsets.ProfessionalViewSet, basename="professional")

urlpatterns = [
    path("", include(router.urls)),
]
