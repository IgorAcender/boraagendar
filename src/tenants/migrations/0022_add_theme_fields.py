# Generated migration for theme fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0021_brandingsettings_sections_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='theme_template',
            field=models.CharField(
                choices=[('custom', 'Personalizado'), ('dark', 'Preto e Branco (Tema Escuro)'), ('light', 'Branco e Preto (Tema Claro)')],
                default='custom',
                help_text='Escolha um modelo pré-configurado ou personalize as cores',
                max_length=20,
                verbose_name='Modelo de Tema'
            ),
        ),
        migrations.AddField(
            model_name='tenant',
            name='background_color',
            field=models.CharField(
                default='#000000',
                max_length=7,
                verbose_name='Cor de Fundo'
            ),
        ),
        migrations.AddField(
            model_name='tenant',
            name='text_color',
            field=models.CharField(
                default='#FFFFFF',
                max_length=7,
                verbose_name='Cor do Texto'
            ),
        ),
        migrations.AddField(
            model_name='tenant',
            name='button_color',
            field=models.CharField(
                default='#22c55e',
                max_length=7,
                verbose_name='Cor do Botão'
            ),
        ),
        migrations.AddField(
            model_name='tenant',
            name='button_text_color',
            field=models.CharField(
                default='#FFFFFF',
                max_length=7,
                verbose_name='Cor do Texto do Botão'
            ),
        ),
    ]
