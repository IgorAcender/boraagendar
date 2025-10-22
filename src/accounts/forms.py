from __future__ import annotations

from typing import Tuple

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.utils.text import slugify

from tenants.models import Tenant, TenantMembership

User = get_user_model()


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "seu@exemplo.com"}),
    )


class SignupForm(forms.Form):
    company_name = forms.CharField(label="Nome da empresa", max_length=150)
    company_slug = forms.SlugField(
        label="Endereço público",
        max_length=150,
        required=False,
        help_text="Usado na URL pública: /agendar/<endereco>/",
    )
    full_name = forms.CharField(label="Seu nome", max_length=150)
    email = forms.EmailField(label="E-mail")
    phone_number = forms.CharField(label="Telefone", max_length=32, required=False)
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirme a senha", widget=forms.PasswordInput)

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe um usuário com este e-mail.")
        return email

    def clean_company_slug(self) -> str:
        name = self.cleaned_data.get("company_name", "")
        slug = self.cleaned_data.get("company_slug") or name
        slug = slugify(slug)
        if not slug:
            raise forms.ValidationError("Informe um endereço válido.")
        if Tenant.objects.filter(slug=slug).exists():
            raise forms.ValidationError("Este endereço já está em uso.")
        return slug

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "As senhas não conferem.")
        return cleaned_data

    @transaction.atomic
    def save(self) -> Tuple[User, Tenant]:
        data = self.cleaned_data
        first_name, last_name = _split_full_name(data["full_name"])

        user = User.objects.create_user(
            email=data["email"],
            password=data["password1"],
            first_name=first_name,
            last_name=last_name,
            phone_number=data.get("phone_number", ""),
        )

        tenant = Tenant.objects.create(
            name=data["company_name"],
            slug=data["company_slug"],
            email=data["email"],
            phone_number=data.get("phone_number", ""),
        )

        TenantMembership.objects.create(
            tenant=tenant,
            user=user,
            role=TenantMembership.Role.OWNER,
        )

        return user, tenant


def _split_full_name(value: str) -> Tuple[str, str]:
    parts = value.strip().split(" ", 1)
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name
