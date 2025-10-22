from __future__ import annotations

import secrets
from typing import Tuple

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import TenantMembership

User = get_user_model()


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
