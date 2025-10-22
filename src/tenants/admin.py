from django.contrib import admin

from .models import Tenant, TenantMembership


class TenantMembershipInline(admin.TabularInline):
    model = TenantMembership
    extra = 0
    autocomplete_fields = ("user",)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug", "email")
    list_filter = ("is_active", "timezone")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TenantMembershipInline]


@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ("tenant", "user", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "tenant")
    search_fields = ("tenant__name", "user__email", "user__first_name", "user__last_name")
