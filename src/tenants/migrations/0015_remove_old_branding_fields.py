# Generated migration to simplify BrandingSettings model
# Removes button_color_secondary, use_gradient_buttons, highlight_color
# Keeps only: background_color, text_color, button_color_primary, button_text_color

from django.db import migrations


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
