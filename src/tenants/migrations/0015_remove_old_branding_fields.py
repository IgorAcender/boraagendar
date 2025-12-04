# Generated migration to simplify BrandingSettings model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0014_brandingsettings_button_text_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brandingsettings',
            name='button_color_secondary',
        ),
        migrations.RemoveField(
            model_name='brandingsettings',
            name='use_gradient_buttons',
        ),
        migrations.RemoveField(
            model_name='brandingsettings',
            name='highlight_color',
        ),
    ]
