from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from django.test import TestCase

from scheduling.models import AvailabilityRule, Booking, Professional, Service
from scheduling.services.availability import AvailabilityService
from tenants.models import Tenant


class AvailabilityServiceTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Barbearia Teste", slug="barbearia-teste")
        self.service = Service.objects.create(
            tenant=self.tenant,
            name="Corte",
            duration_minutes=30,
            price=100,
            is_active=True,
        )
        self.professional = Professional.objects.create(tenant=self.tenant, display_name="Joao")
        self.service.professionals.add(self.professional)
        self.target_date = date(2025, 1, 6)  # segunda-feira
        AvailabilityRule.objects.create(
            tenant=self.tenant,
            professional=self.professional,
            weekday=self.target_date.weekday(),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

    def test_generates_expected_slots(self):
        availability = AvailabilityService(self.tenant)
        slots = availability.get_available_slots(self.service, self.professional, self.target_date)
        self.assertEqual(len(slots), 3)
        self.assertEqual(slots[0].start.time(), time(9, 0))
        self.assertEqual(slots[-1].end.time(), time(10, 0))

    def test_detects_booked_slot(self):
        tz = ZoneInfo(self.tenant.timezone)
        scheduled_for = datetime.combine(self.target_date, time(9, 0), tzinfo=tz)
        Booking.objects.create(
            tenant=self.tenant,
            service=self.service,
            professional=self.professional,
            customer_name="Cliente",
            customer_phone="11999999999",
            scheduled_for=scheduled_for,
            duration_minutes=30,
            price=100,
        )
        availability = AvailabilityService(self.tenant)
        self.assertFalse(availability.is_slot_available(self.service, self.professional, scheduled_for))
        slots = availability.get_available_slots(self.service, self.professional, self.target_date)
        # primeiro intervalo continua, mas o horario das 9h nao deve mais aparecer
        self.assertTrue(all(slot.start != scheduled_for for slot in slots))
