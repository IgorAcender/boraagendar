from __future__ import annotations

import base64
import secrets
from typing import Tuple

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

from .models import Tenant, TenantMembership, BrandingSettings

User = get_user_model()


class TenantUpdateForm(forms.ModelForm):
    """Formulário para o dono editar informações da empresa"""

    def save(self, commit=True):
        # Converter foto para base64 se houver upload NOVO
        avatar = self.cleaned_data.get("avatar")

        # Verificar se é um upload novo (UploadedFile) ou arquivo já existente (FieldFile)
        from django.core.files.uploadedfile import UploadedFile

        if avatar and isinstance(avatar, UploadedFile):
            # É um upload novo - converter para base64
            avatar_data = avatar.read()
            avatar_base64 = base64.b64encode(avatar_data).decode('utf-8')
            # Adicionar o prefixo do tipo MIME
            content_type = avatar.content_type or 'image/jpeg'
            self.instance.avatar_base64 = f"data:{content_type};base64,{avatar_base64}"
            # Limpar o campo avatar para não tentar salvar no disco
            self.instance.avatar = None

        return super().save(commit=commit)

    class Meta:
        model = Tenant
        fields = [
            "name",
            "slug",
            "document",
            "phone_number",
            "whatsapp_number",
            "email",
            "color_primary",
            "color_secondary",
            "avatar",
            "label_servico",
            "label_servico_plural",
            "label_profissional",
            "label_profissional_plural",
            "slot_interval_minutes",
        ]
        labels = {
            "name": "Nome da Empresa",
            "slug": "URL de Agendamento (Slug)",
            "document": "CNPJ/CPF",
            "phone_number": "Telefone",
            "whatsapp_number": "WhatsApp",
            "email": "E-mail",
            "color_primary": "Cor Primária",
            "color_secondary": "Cor Secundária",
            "avatar": "Logo da Empresa",
            "label_servico": "Singular",
            "label_servico_plural": "Plural",
            "label_profissional": "Singular",
            "label_profissional_plural": "Plural",
            "slot_interval_minutes": "Intervalo entre horários",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome da sua empresa"}),
            "slug": forms.TextInput(attrs={"class": "form-control slug-input", "placeholder": "minha-empresa"}),
            "document": forms.TextInput(attrs={"class": "form-control", "placeholder": "00.000.000/0000-00"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "(00) 0000-0000"}),
            "whatsapp_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "(00) 00000-0000"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "contato@empresa.com"}),
            "color_primary": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            "color_secondary": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
            "label_servico": forms.TextInput(attrs={"class": "form-control", "placeholder": "Serviço"}),
            "label_servico_plural": forms.TextInput(attrs={"class": "form-control", "placeholder": "Serviços"}),
            "label_profissional": forms.TextInput(attrs={"class": "form-control", "placeholder": "Profissional"}),
            "label_profissional_plural": forms.TextInput(attrs={"class": "form-control", "placeholder": "Profissionais"}),
            "slot_interval_minutes": forms.Select(attrs={"class": "form-control"}),
        }
        help_texts = {
            "name": "Nome que aparece na interface e para os clientes",
            "slug": "⚠️ CUIDADO: Mudar isso altera a URL pública! Links antigos param de funcionar.",
            "color_primary": "Cor principal da interface",
            "color_secondary": "Cor secundária da interface",
            "label_servico": "Ex: Serviço, Modalidade, Tipo de Evento",
            "label_servico_plural": "Ex: Serviços, Modalidades, Tipos de Eventos",
            "label_profissional": "Ex: Profissional, Quadra, Salão",
            "label_profissional_plural": "Ex: Profissionais, Quadras, Salões",
            "slot_interval_minutes": "Controle de espaçamento entre os horários disponíveis na agenda pública.",
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


class BrandingSettingsForm(forms.ModelForm):
    """Formulário para personalização de cores do tenant"""

    hero_image = forms.FileField(
        label="Foto de capa / hero do mini site",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        help_text="Imagem exibida no topo do mini site. Formatos: JPG/PNG."
    )
    about_us = forms.CharField(
        label="Sobre nós (mini site)",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Fale sobre seu negócio"}),
        help_text="Texto que aparece na seção Sobre nós do mini site."
    )
    contact_info = forms.CharField(
        label="Contatos (mini site)",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Telefone, WhatsApp, e-mail..."}),
        help_text="Informações de contato exibidas no mini site."
    )

    def __init__(self, *args, tenant: Tenant, **kwargs):
        self.tenant = tenant
        super().__init__(*args, **kwargs)
        # Preenche campo extra com valor do tenant
        self.fields["about_us"].initial = tenant.about_us
        self.fields["contact_info"].initial = tenant.contact_info

    class Meta:
        model = BrandingSettings
        fields = [
            "background_color",
            "text_color",
            "button_color_primary",
            "button_color_secondary",
            "button_text_color",
            "use_gradient_buttons",
            "highlight_color",
            "hero_image",  # campo extra (não no modelo)
            "about_us",    # campo extra (não no modelo)
            "contact_info",  # campo extra (não no modelo)
        ]
        labels = {
            "background_color": "Cor de Fundo",
            "text_color": "Cor de Texto",
            "button_color_primary": "Cor Primária do Botão",
            "button_color_secondary": "Cor Secundária do Botão",
            "button_text_color": "Cor de Texto dos Botões",
            "use_gradient_buttons": "Usar Gradiente nos Botões",
            "highlight_color": "Cor de Destaque",
            "hero_image": "Foto de capa / hero",
            "about_us": "Sobre nós (mini site)",
            "contact_info": "Contatos (mini site)",
        }
        widgets = {
            "background_color": forms.TextInput(attrs={"type": "color", "class": "form-control color-picker"}),
            "text_color": forms.TextInput(attrs={"type": "color", "class": "form-control color-picker"}),
            "button_color_primary": forms.TextInput(attrs={"type": "color", "class": "form-control color-picker"}),
            "button_color_secondary": forms.TextInput(attrs={"type": "color", "class": "form-control color-picker"}),
            "button_text_color": forms.TextInput(attrs={"type": "color", "class": "form-control color-picker"}),
            "use_gradient_buttons": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "highlight_color": forms.TextInput(attrs={"type": "color", "class": "form-control color-picker"}),
        }
        help_texts = {
            "background_color": "Define o fundo de todas as páginas",
            "text_color": "Cor padrão do texto em todas as páginas",
            "button_color_primary": "Cor principal dos botões",
            "button_color_secondary": "Cor secundária (usada em gradientes)",
            "button_text_color": "Cor do texto dentro dos botões",
            "use_gradient_buttons": "Se ativado, os botões terão gradiente com as duas cores",
            "highlight_color": "Cor para destaque (textos especiais, ícones, contornos)",
            "hero_image": "Selecione uma imagem para o topo do mini site",
            "about_us": "Texto exibido na seção Sobre nós do mini site",
            "contact_info": "Telefone/WhatsApp/e-mail exibidos na seção de contato do mini site",
        }

    def save(self, commit=True):
        branding = super().save(commit=commit)

        hero = self.cleaned_data.get("hero_image")
        if hero and isinstance(hero, UploadedFile):
            hero_data = hero.read()
            hero_b64 = base64.b64encode(hero_data).decode("utf-8")
            content_type = hero.content_type or "image/jpeg"
            self.tenant.avatar_base64 = f"data:{content_type};base64,{hero_b64}"
            self.tenant.avatar = None  # evita salvar no disco
            self.tenant.save(update_fields=["avatar", "avatar_base64", "updated_at"])

        about_us = self.cleaned_data.get("about_us")
        if about_us is not None:
            self.tenant.about_us = about_us
            self.tenant.save(update_fields=["about_us", "updated_at"])

        contact_info = self.cleaned_data.get("contact_info")
        if contact_info is not None:
            self.tenant.contact_info = contact_info
            self.tenant.save(update_fields=["contact_info", "updated_at"])

        return branding
