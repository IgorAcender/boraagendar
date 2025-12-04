# Generated migration for BrandingSettings

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tenants", "0012_tenant_about_us_tenant_address_tenant_amenities_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BrandingSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("background_color", models.CharField(default="#0F172A", help_text="Cor de fundo de todas as páginas", max_length=7, verbose_name="Cor de Fundo")),
                ("text_color", models.CharField(default="#E2E8F0", help_text="Cor padrão do texto/fontes", max_length=7, verbose_name="Cor de Texto")),
                ("button_color_primary", models.CharField(default="#667EEA", help_text="Cor primária dos botões e destaque", max_length=7, verbose_name="Cor Primária do Botão")),
                ("button_color_secondary", models.CharField(default="#764BA2", help_text="Cor secundária (para gradientes)", max_length=7, verbose_name="Cor Secundária do Botão")),
                ("use_gradient_buttons", models.BooleanField(default=True, help_text="Se ativado, botões usarão gradiente com as duas cores. Se desativado, usa apenas a cor primária.", verbose_name="Usar Gradiente nos Botões")),
                ("highlight_color", models.CharField(default="#FBBF24", help_text="Cor para textos em destaque, ícones destacados, contornos especiais", max_length=7, verbose_name="Cor de Destaque")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Atualizado em")),
                ("tenant", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="branding_settings", to="tenants.tenant", verbose_name="Empresa")),
            ],
            options={
                "verbose_name": "Configuração de Marca",
                "verbose_name_plural": "Configurações de Marca",
            },
        ),
    ]
