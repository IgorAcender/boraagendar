# Generated migration for theme template field in BrandingSettings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0021_brandingsettings_sections_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='brandingsettings',
            name='theme_template',
            field=models.CharField(
                choices=[('custom', 'Personalizado'), ('dark', 'Preto e Branco (Tema Escuro)'), ('light', 'Branco e Preto (Tema Claro)')],
                default='custom',
                help_text='Escolha um modelo pré-configurado ou personalize as cores',
                max_length=20,
                verbose_name='Modelo de Tema'
            ),
        ),
    ]
