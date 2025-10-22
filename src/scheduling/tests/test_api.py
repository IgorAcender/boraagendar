from datetime import datetime
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from scheduling.models import Booking, Professional, Service
from tenants.models import Tenant, TenantMembership

User = get_user_model()


class BookingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="owner@example.com", password="pass123")
        self.tenant = Tenant.objects.create(name="Studio 1", slug="studio-1")
        TenantMembership.objects.create(
            tenant=self.tenant,
            user=self.user,
            role=TenantMembership.Role.OWNER,
            is_active=True,
        )
        self.service = Service.objects.create(
            tenant=self.tenant,
            name="Corte",
            duration_minutes=30,
            price=80,
        )
        self.professional = Professional.objects.create(tenant=self.tenant, display_name="Ana")
        self.service.professionals.add(self.professional)
        scheduled_for = datetime(2025, 1, 6, 9, 0, tzinfo=ZoneInfo(self.tenant.timezone))
        Booking.objects.create(
            tenant=self.tenant,
            service=self.service,
            professional=self.professional,
            customer_name="Cliente A",
            customer_phone="11999999999",
            scheduled_for=scheduled_for,
            duration_minutes=30,
            price=80,
        )

        other_tenant = Tenant.objects.create(name="Studio 2", slug="studio-2")
        other_service = Service.objects.create(
            tenant=other_tenant,
            name="Barba",
            duration_minutes=30,
            price=90,
        )
        other_professional = Professional.objects.create(tenant=other_tenant, display_name="Beatriz")
        other_service.professionals.add(other_professional)
        other_scheduled = datetime(2025, 1, 6, 10, 0, tzinfo=ZoneInfo(other_tenant.timezone))
        Booking.objects.create(
            tenant=other_tenant,
            service=other_service,
            professional=other_professional,
            customer_name="Cliente B",
            customer_phone="11988887777",
            scheduled_for=other_scheduled,
            duration_minutes=30,
            price=90,
        )

    def test_list_bookings_scoped_to_membership(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/bookings/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]
        self.assertEqual(result["customer_name"], "Cliente A")
