from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Configurações SaaS", {"fields": ("phone_number", "locale", "timezone")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff", "is_superuser")
