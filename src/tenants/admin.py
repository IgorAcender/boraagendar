from django.contrib import admin

from .models import Tenant, TenantMembership, BusinessHours, BrandingSettings
from .models_subscription import Plan, Subscription, FeatureUsage


class TenantMembershipInline(admin.TabularInline):
    model = TenantMembership
    extra = 0
    autocomplete_fields = ("user",)


class BusinessHoursInline(admin.TabularInline):
    model = BusinessHours
    extra = 0
    fields = ("day_of_week", "is_closed", "opening_time", "closing_time")


class BrandingSettingsInline(admin.StackedInline):
    model = BrandingSettings
    extra = 0
    fields = (
        "background_color", "text_color",
        "button_color_primary", "button_color_secondary", "use_gradient_buttons",
        "button_text_color"
    )


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug", "email")
    list_filter = ("is_active", "timezone")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [BrandingSettingsInline, TenantMembershipInline, BusinessHoursInline]
    fieldsets = (
        ("Informações Básicas", {
            "fields": ("name", "slug", "document", "timezone", "is_active")
        }),
        ("Contato", {
            "fields": ("phone_number", "whatsapp_number", "email")
        }),
        ("Aparência", {
            "fields": ("avatar", "color_primary", "color_secondary")
        }),
        ("Configurações de Serviços", {
            "fields": (
                "label_servico", "label_servico_plural",
                "label_profissional", "label_profissional_plural",
                "slot_interval_minutes"
            )
        }),
        ("Página de Landing", {
            "fields": (
                "about_us", "address", "neighborhood", "city", "state", "zip_code",
                "instagram_url", "facebook_url", "payment_methods", "amenities"
            ),
            "description": "Configure as informações que aparecem na página de landing do seu negócio."
        }),
    )

@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ("tenant", "user", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "tenant")
    search_fields = ("tenant__name", "user__email", "user__first_name", "user__last_name")


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ("tenant", "day_of_week", "is_closed", "opening_time", "closing_time")
    list_filter = ("tenant", "day_of_week", "is_closed")
    search_fields = ("tenant__name",)


@admin.register(BrandingSettings)
class BrandingSettingsAdmin(admin.ModelAdmin):
    list_display = ("tenant", "background_color", "text_color", "button_color_primary")
    search_fields = ("tenant__name",)
    fieldsets = (
        ("Cores Gerais", {
            "fields": ("tenant", "background_color", "text_color")
        }),
        ("Botão e Ícones", {
            "fields": ("button_color_primary", "button_color_secondary", "use_gradient_buttons", "button_text_color")
        }),
    )


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price_monthly', 'is_active')
    list_filter = ('is_active', 'plan_type')
    search_fields = ('name', 'slug')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('slug', 'name', 'description', 'plan_type')
        }),
        ('Preços', {
            'fields': ('price_monthly', 'price_annual')
        }),
        ('Limites', {
            'fields': ('max_professionals', 'max_services', 'max_monthly_bookings')
        }),
        ('Features', {
            'fields': (
                'has_dashboard', 'has_financial_module', 'has_advanced_analytics',
                'has_sms_notifications', 'has_email_campaigns', 'has_customer_reviews',
                'has_custom_domain', 'has_api_access', 'has_white_label'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'plan', 'status', 'billing_cycle', 'trial_ends_at')
    list_filter = ('status', 'billing_cycle', 'created_at')
    search_fields = ('tenant__name', 'stripe_customer_id')
    readonly_fields = ('created_at', 'updated_at', 'started_at')
    
    fieldsets = (
        ('Vínculo', {
            'fields': ('tenant', 'plan')
        }),
        ('Status', {
            'fields': ('status', 'billing_cycle', 'auto_renew')
        }),
        ('Datas', {
            'fields': ('trial_started_at', 'trial_ends_at', 'next_billing_date', 'cancelled_at')
        }),
        ('Pagamento', {
            'fields': ('payment_method', 'stripe_customer_id', 'stripe_subscription_id')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FeatureUsage)
class FeatureUsageAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'feature_name', 'monthly_usage', 'monthly_limit')
    list_filter = ('feature_name', 'reset_date')
    search_fields = ('subscription__tenant__name', 'feature_name')
