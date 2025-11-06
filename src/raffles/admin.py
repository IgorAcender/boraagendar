from django.contrib import admin

from . import models


@admin.register(models.Raffle)
class RaffleAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "status", "total_numbers", "numbers_available", "created_at")
    list_filter = ("status", "tenant")
    search_fields = ("name", "slug", "tenant__name")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.RaffleOrder)
class RaffleOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "raffle",
        "user",
        "status",
        "quantity",
        "amount",
        "payment_method",
        "created_at",
    )
    list_filter = ("status", "payment_method", "raffle__tenant")
    search_fields = ("id", "user__email", "raffle__name")
    autocomplete_fields = ("raffle", "user")


@admin.register(models.ReferralInvitation)
class ReferralInvitationAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "raffle",
        "inviter",
        "invitee",
        "status",
        "clicks",
        "inviter_bonus_allocated",
        "created_at",
    )
    list_filter = ("status", "raffle__tenant", "inviter_bonus_allocated")
    search_fields = ("code", "inviter__email", "invitee__email")
    readonly_fields = ("created_at", "redeemed_at", "last_clicked_at")
    autocomplete_fields = ("raffle", "inviter", "invitee")


@admin.register(models.RaffleTicketAllocation)
class RaffleTicketAllocationAdmin(admin.ModelAdmin):
    list_display = ("raffle", "number", "user", "source", "order", "referral", "allocated_at")
    list_filter = ("raffle__tenant", "source")
    search_fields = ("raffle__name", "user__email", "number")
    autocomplete_fields = ("raffle", "user", "order", "referral")

