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
    # Campos para editar dados do usuário vinculado
    user_full_name = forms.CharField(label="Nome completo", max_length=150, required=False)
    user_email = forms.EmailField(label="E-mail", required=False)
    user_phone_number = forms.CharField(label="Telefone", max_length=32, required=False)
    user_password = forms.CharField(label="Nova senha (deixe em branco para manter a atual)", widget=forms.PasswordInput, required=False)

    class Meta:
        model = Professional
        fields = ["user", "display_name", "photo", "bio", "color", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Preencher campos com dados do usuário atual se existir
        if self.instance and self.instance.pk and self.instance.user:
            user = self.instance.user
            self.fields["user_full_name"].initial = user.get_full_name()
            self.fields["user_email"].initial = user.email
            self.fields["user_phone_number"].initial = user.phone_number

    def clean_user_email(self):
        email = self.cleaned_data.get("user_email", "").strip()
        if email:
            User = get_user_model()
            # Verificar se o email já existe (exceto o usuário atual)
            existing_user = User.objects.filter(email=email).first()
            if existing_user and self.instance.user and existing_user.pk != self.instance.user.pk:
                raise ValidationError("Este e-mail já está em uso por outro usuário.")
        return email

    def save(self, commit=True):
        # Atualizar dados do usuário ANTES de salvar o professional
        if self.instance.user:
            user = self.instance.user

            # Atualizar nome completo
            full_name = self.cleaned_data.get("user_full_name", "").strip()
            if full_name:
                name_parts = full_name.split(" ", 1)
                user.first_name = name_parts[0]
                user.last_name = name_parts[1] if len(name_parts) > 1 else ""

            # Atualizar email
            email = self.cleaned_data.get("user_email", "").strip()
            if email:
                user.email = email

            # Atualizar telefone
            phone = self.cleaned_data.get("user_phone_number", "").strip()
            if phone:
                user.phone_number = phone

            # Atualizar senha se fornecida
            password = self.cleaned_data.get("user_password", "").strip()
            if password:
                user.set_password(password)

            if commit:
                user.save()

        # Agora salva o professional normalmente (incluindo arquivos como photo)
        return super().save(commit=commit)



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
