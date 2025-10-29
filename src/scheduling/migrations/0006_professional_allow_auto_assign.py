from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scheduling", "0005_service_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="professional",
            name="allow_auto_assign",
            field=models.BooleanField(
                default=True,
                help_text="Quando marcado, este profissional pode ser escolhido automaticamente na opção Sem preferência.",
                verbose_name="Disponível para seleção automática",
            ),
        ),
    ]

