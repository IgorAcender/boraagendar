from django.urls import include, path
from rest_framework.routers import DefaultRouter

from scheduling.api import viewsets as scheduling_viewsets
from raffles.api import viewsets as raffles_viewsets
from financial.views import AccountViewSet, TransactionViewSet, CommissionViewSet
from . import api as config_api

router = DefaultRouter()
router.register(r"bookings", scheduling_viewsets.BookingViewSet, basename="booking")
router.register(r"services", scheduling_viewsets.ServiceViewSet, basename="service")
router.register(r"professionals", scheduling_viewsets.ProfessionalViewSet, basename="professional")
router.register(r"raffles", raffles_viewsets.RaffleViewSet, basename="raffle")
router.register(r"raffle-orders", raffles_viewsets.RaffleOrderViewSet, basename="raffle-order")
router.register(r"raffle-referrals", raffles_viewsets.ReferralInvitationViewSet, basename="raffle-referral")
router.register(r"financial/accounts", AccountViewSet, basename="account")
router.register(r"financial/transactions", TransactionViewSet, basename="transaction")
router.register(r"financial/commissions", CommissionViewSet, basename="commission")

urlpatterns = [
    # Dashboard stats endpoint (used by React SPA)
    path("dashboard/stats/", config_api.dashboard_stats, name="dashboard-stats"),
    path("dashboard/stats/series/", config_api.dashboard_stats_series, name="dashboard-stats-series"),
    path("", include(router.urls)),
]
