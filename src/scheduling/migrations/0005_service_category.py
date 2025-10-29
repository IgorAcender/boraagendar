from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scheduling", "0004_alter_booking_professional"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="category",
            field=models.CharField(blank=True, max_length=120, verbose_name="Categoria"),
        ),
    ]

