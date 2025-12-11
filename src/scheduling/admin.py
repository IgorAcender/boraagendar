from django.contrib import admin

from .models import AvailabilityRule, Booking, Professional, ProfessionalService, Service, TimeOff, Target


class ProfessionalServiceInline(admin.TabularInline):
    model = ProfessionalService
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "tenant", "duration_minutes", "price", "is_active")
    list_filter = ("tenant", "category", "is_active")
    search_fields = ("name", "tenant__name")


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ("display_name", "tenant", "is_active", "allow_auto_assign")
    list_filter = ("tenant", "is_active", "allow_auto_assign")
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


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ("tenant", "get_period_label", "get_target_type_label", "target_value", "is_active")
    list_filter = ("tenant", "period", "target_type", "is_active")
    search_fields = ("tenant__name", "description")
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('tenant', 'period', 'target_type', 'target_value', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


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

