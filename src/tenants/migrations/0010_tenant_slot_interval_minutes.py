from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenants", "0002_alter_tenantmembership_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenant",
            name="slot_interval_minutes",
            field=models.PositiveIntegerField(
                choices=[
                    (5, "5 minutos"),
                    (10, "10 minutos"),
                    (15, "15 minutos"),
                    (20, "20 minutos"),
                    (30, "30 minutos"),
                    (45, "45 minutos"),
                    (60, "60 minutos"),
                ],
                default=15,
                help_text="Define de quantos em quantos minutos os horários aparecem no agendamento público.",
                verbose_name="Intervalo entre horários (min)",
            ),
        ),
    ]
