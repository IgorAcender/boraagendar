from datetime import date, datetime
from decimal import Decimal

from django import forms
from django.core.exceptions import FieldError, ValidationError
from django.contrib.auth import get_user_model
import secrets

from tenants.models import Tenant, TenantMembership

from .models import Booking, Professional, Service
from .services.availability import AvailabilityService


class TenantAwareForm(forms.ModelForm):
    def __init__(self, *args, tenant: Tenant, **kwargs):
        self.tenant = tenant
        super().__init__(*args, **kwargs)
        self._limit_queryset_fields()

    def _limit_queryset_fields(self) -> None:
        for field in self.fields.values():
            if hasattr(field, "queryset") and field.queryset is not None:
                try:
                    field.queryset = field.queryset.filter(tenant=self.tenant)
                except (FieldError, TypeError, AttributeError):
                    model = getattr(field.queryset, "model", None)
                    if model and model.__name__ == "User":
                        field.queryset = field.queryset.filter(
                            tenant_memberships__tenant=self.tenant, tenant_memberships__is_active=True
                        )


class AvailabilitySearchForm(forms.Form):
    service = forms.ModelChoiceField(label="Servico", queryset=Service.objects.none())
    professional = forms.ModelChoiceField(
        label="Profissional",
        queryset=Professional.objects.none(),
        required=False,
    )
    date = forms.DateField(label="Data", initial=date.today)

    def __init__(self, *args, tenant: Tenant, **kwargs):
        self.tenant = tenant
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(tenant=tenant, is_active=True).order_by("name")
        self.fields["professional"].queryset = Professional.objects.filter(
            tenant=tenant, is_active=True
        ).order_by("display_name")


class ServiceForm(TenantAwareForm):
    class Meta:
        model = Service
        fields = ["name", "description", "duration_minutes", "price", "is_active", "professionals"]


class ProfessionalForm(TenantAwareForm):
    # Campos opcionais para criar um novo usuário do zero
    create_user = forms.BooleanField(label="Criar novo usuário", required=False)
    new_user_full_name = forms.CharField(label="Nome completo", max_length=150, required=False)
    new_user_email = forms.EmailField(label="E-mail do usuário", required=False)
    new_user_phone_number = forms.CharField(label="Telefone", max_length=32, required=False)
    new_user_password = forms.CharField(label="Senha inicial (opcional)", widget=forms.PasswordInput, required=False)

    class Meta:
        model = Professional
        fields = ["user", "display_name", "photo", "bio", "color", "is_active"]


class ProfessionalUpdateForm(TenantAwareForm):
    class Meta:
        model = Professional
        fields = ["user", "display_name", "photo", "bio", "color", "is_active"]



class BookingForm(TenantAwareForm):
    date = forms.DateField(label="Data", initial=date.today)
    time = forms.TimeField(label="Hora")

    class Meta:
        model = Booking
        fields = [
            "service",
            "professional",
            "customer_name",
            "customer_phone",
            "customer_email",
            "date",
            "time",
            "notes",
        ]

    def __init__(self, *args, tenant: Tenant, hide_schedule_fields: bool = False, **kwargs):
        self.hide_schedule_fields = hide_schedule_fields
        super().__init__(*args, tenant=tenant, **kwargs)
        if hide_schedule_fields:
            for name in ("service", "professional", "date", "time"):
                self.fields[name].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get("service")
        date_value = cleaned_data.get("date")
        time_value = cleaned_data.get("time")
        professional = cleaned_data.get("professional")

        if self.instance.pk:
            return cleaned_data

        if service and date_value and time_value:
            availability_service = AvailabilityService(tenant=self.tenant)
            target_datetime = datetime.combine(date_value, time_value)
            if not availability_service.is_slot_available(service, professional, target_datetime):
                raise forms.ValidationError("Este horario nao esta disponivel.")
            cleaned_data["scheduled_for"] = target_datetime
            cleaned_data["duration_minutes"] = service.duration_for(professional)
            cleaned_data["price"] = service.price_for(professional)
        return cleaned_data

    def save(self, commit=True):
        self.instance.scheduled_for = self.cleaned_data.get("scheduled_for", self.instance.scheduled_for)
        duration_default = self.instance.duration_minutes
        price_default = self.instance.price
        if self.instance.service and self.instance.professional:
            duration_default = self.instance.service.duration_for(self.instance.professional)
            price_default = self.instance.service.price_for(self.instance.professional)
        if duration_default is None and self.instance.service:
            duration_default = self.instance.service.duration_minutes
        if price_default is None and self.instance.service:
            price_default = self.instance.service.price
        self.instance.duration_minutes = self.cleaned_data.get("duration_minutes") or duration_default or 0
        self.instance.price = self.cleaned_data.get("price") or price_default or Decimal("0")
        return super().save(commit=commit)
