from __future__ import annotations

import secrets
from typing import Tuple

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import Tenant, TenantMembership

User = get_user_model()


class TenantUpdateForm(forms.ModelForm):
    """Formulário para o dono editar informações da empresa"""

    class Meta:
        model = Tenant
        fields = [
            "name",
            "slug",
            "document",
            "phone_number",
            "whatsapp_number",
            "email",
            "timezone",
            "color_primary",
            "color_secondary",
            "avatar",
        ]
        labels = {
            "name": "Nome da Empresa",
            "slug": "URL de Agendamento (Slug)",
            "document": "CNPJ/CPF",
            "phone_number": "Telefone",
            "whatsapp_number": "WhatsApp",
            "email": "E-mail",
            "timezone": "Fuso Horário",
            "color_primary": "Cor Primária",
            "color_secondary": "Cor Secundária",
            "avatar": "Logo da Empresa",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome da sua empresa"}),
            "slug": forms.TextInput(attrs={"class": "form-control slug-input", "placeholder": "minha-empresa"}),
            "document": forms.TextInput(attrs={"class": "form-control", "placeholder": "00.000.000/0000-00"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "(00) 0000-0000"}),
            "whatsapp_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "(00) 00000-0000"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "contato@empresa.com"}),
            "timezone": forms.Select(attrs={"class": "form-control"}),
            "color_primary": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            "color_secondary": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "name": "Nome que aparece na interface e para os clientes",
            "slug": "⚠️ CUIDADO: Mudar isso altera a URL pública! Links antigos param de funcionar.",
            "timezone": "Fuso horário usado para os agendamentos",
            "color_primary": "Cor principal da interface",
            "color_secondary": "Cor secundária da interface",
        }


class TeamMemberCreateForm(forms.Form):
    email = forms.EmailField(label="E-mail")
    full_name = forms.CharField(label="Nome completo", max_length=150, required=False)
    phone_number = forms.CharField(label="Telefone", max_length=32, required=False)
    role = forms.ChoiceField(label="Papel", choices=TenantMembership.Role.choices, initial=TenantMembership.Role.PROFESSIONAL)
    is_active = forms.BooleanField(label="Ativo", required=False, initial=True)
    password = forms.CharField(label="Senha inicial (opcional)", widget=forms.PasswordInput, required=False)

    def __init__(self, *args, tenant, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        self.generated_password: str | None = None

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].lower()
        # Se já tem vínculo com este tenant, erro
        if TenantMembership.objects.filter(tenant=self.tenant, user__email__iexact=email).exists():
            raise ValidationError("Este e-mail já está vinculado à empresa.")
        return email

    def clean(self):
        data = super().clean()
        email = data.get("email")
        if not User.objects.filter(email__iexact=email).exists():
            # novo usuário precisa de nome
            if not data.get("full_name"):
                self.add_error("full_name", "Informe o nome do usuário.")
        return data

    def save(self) -> Tuple[User, TenantMembership]:
        data = self.cleaned_data
        email = data["email"].lower()
        role = data["role"]
        is_active = data["is_active"]
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            full_name: str = (data.get("full_name") or "").strip()
            first_name, last_name = (full_name.split(" ", 1) + [""])[:2]
            password = data.get("password") or secrets.token_urlsafe(12)
            self.generated_password = data.get("password") or password
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name if last_name else "",
                phone_number=data.get("phone_number") or "",
            )

        membership = TenantMembership.objects.create(
            tenant=self.tenant,
            user=user,
            role=role,
            is_active=is_active,
        )
        return user, membership


class TeamMemberUpdateForm(forms.ModelForm):
    class Meta:
        model = TenantMembership
        fields = ["role", "is_active"]
