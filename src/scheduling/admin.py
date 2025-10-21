from django.contrib import admin

from .models import AvailabilityRule, Booking, Professional, ProfessionalService, Service, TimeOff


class ProfessionalServiceInline(admin.TabularInline):
    model = ProfessionalService
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "duration_minutes", "price", "is_active")
    list_filter = ("tenant", "is_active")
    search_fields = ("name", "tenant__name")


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ("display_name", "tenant", "is_active")
    list_filter = ("tenant", "is_active")
    search_fields = ("display_name", "tenant__name")
    inlines = [ProfessionalServiceInline]


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = ("tenant", "professional", "weekday", "start_time", "end_time", "is_active")
    list_filter = ("tenant", "professional", "weekday", "is_active")


@admin.register(TimeOff)
class TimeOffAdmin(admin.ModelAdmin):
    list_display = ("tenant", "professional", "name", "start", "end")
    list_filter = ("tenant", "professional")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "service",
        "professional",
        "customer_name",
        "scheduled_for",
        "status",
    )
    list_filter = ("tenant", "professional", "status")
    search_fields = ("customer_name", "customer_phone", "service__name")
