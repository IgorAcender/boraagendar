from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List, Optional
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db.models import Q

from scheduling.models import (
    AvailabilityRule,
    Booking,
    Professional,
    ProfessionalService,
    Service,
    TimeOff,
)


@dataclass(frozen=True)
class AvailableSlot:
    professional: Professional
    start: datetime
    end: datetime


class AvailabilityService:
    slot_granularity = timedelta(minutes=15)

    def __init__(self, tenant):
        self.tenant = tenant
        self.timezone = ZoneInfo(tenant.timezone or settings.TIME_ZONE)

    def get_available_slots(
        self, service: Service, professional: Optional[Professional], target_date
    ) -> List[AvailableSlot]:
        professionals = [professional] if professional else list(self._professionals_for_service(service))
        slots: List[AvailableSlot] = []
        for prof in professionals:
            slots.extend(self._slots_for_professional(service, prof, target_date))
        slots.sort(key=lambda slot: (slot.start, slot.professional.display_name))
        return slots

    def is_slot_available(
        self, service: Service, professional: Optional[Professional], start: datetime
    ) -> bool:
        professionals: Iterable[Professional]
        if professional:
            professionals = [professional]
        else:
            professionals = self._professionals_for_service(service)

        for prof in professionals:
            duration = self._service_duration(service, prof)
            end = start + timedelta(minutes=duration)
            if not self._is_within_availability(prof, start, end):
                continue
            if self._has_conflict(prof, start, end):
                continue
            return True
        return False

    def _slots_for_professional(self, service: Service, professional: Professional, target_date) -> List[AvailableSlot]:
        duration = self._service_duration(service, professional)
        intervals = self._availability_intervals(professional, target_date)
        slots: List[AvailableSlot] = []

        for start, end in intervals:
            slot_start = start
            while slot_start + timedelta(minutes=duration) <= end:
                slot_end = slot_start + timedelta(minutes=duration)
                if not self._has_conflict(professional, slot_start, slot_end):
                    slots.append(AvailableSlot(professional=professional, start=slot_start, end=slot_end))
                slot_start += self.slot_granularity
        return slots

    def _availability_intervals(self, professional: Professional, target_date) -> List[tuple[datetime, datetime]]:
        weekday = target_date.weekday()
        rules = AvailabilityRule.objects.filter(
            tenant=self.tenant,
            weekday=weekday,
            is_active=True,
        ).filter(Q(professional__isnull=True) | Q(professional=professional))

        intervals: List[tuple[datetime, datetime]] = []
        for rule in rules:
            start_dt = datetime.combine(target_date, rule.start_time, tzinfo=self.timezone)
            end_dt = datetime.combine(target_date, rule.end_time, tzinfo=self.timezone)
            if start_dt >= end_dt:
                continue
            segments = [(start_dt, end_dt)]
            if rule.break_start and rule.break_end:
                break_start = datetime.combine(target_date, rule.break_start, tzinfo=self.timezone)
                break_end = datetime.combine(target_date, rule.break_end, tzinfo=self.timezone)
                segments = [
                    (start_dt, min(break_start, end_dt)),
                    (max(break_end, start_dt), end_dt),
                ]
            for segment in segments:
                if segment[0] < segment[1]:
                    intervals.append(segment)
        return intervals

    def _has_conflict(self, professional: Professional, start: datetime, end: datetime) -> bool:
        bookings = Booking.objects.filter(
            tenant=self.tenant,
            professional=professional,
            status__in=[
                Booking.Status.PENDING,
                Booking.Status.CONFIRMED,
                Booking.Status.COMPLETED,
            ],
            scheduled_for__date=start.date(),
        )
        for booking in bookings:
            booking_end = booking.scheduled_for + timedelta(minutes=booking.duration_minutes)
            if start < booking_end and end > booking.scheduled_for:
                return True

        overlapping_time_off = TimeOff.objects.filter(
            tenant=self.tenant,
            start__lt=end,
            end__gt=start,
        ).filter(Q(professional__isnull=True) | Q(professional=professional))
        return overlapping_time_off.exists()

    def _is_within_availability(self, professional: Professional, start: datetime, end: datetime) -> bool:
        date = start.date()
        for available_start, available_end in self._availability_intervals(professional, date):
            if start >= available_start and end <= available_end:
                return True
        return False

    def _service_duration(self, service: Service, professional: Professional) -> int:
        link = ProfessionalService.objects.filter(service=service, professional=professional).first()
        if link and link.duration_minutes:
            return link.duration_minutes
        return service.duration_minutes

    def _professionals_for_service(self, service: Service) -> Iterable[Professional]:
        professionals = service.professionals.filter(is_active=True, tenant=self.tenant)
        if professionals.exists():
            return professionals
        return Professional.objects.filter(tenant=self.tenant, is_active=True)
