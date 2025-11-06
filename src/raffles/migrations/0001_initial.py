from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tenants", "0011_tenant_avatar_base64_tenant_label_profissional_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Raffle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150, verbose_name="Nome")),
                ("slug", models.SlugField(unique=True, verbose_name="Slug")),
                ("description", models.TextField(blank=True, verbose_name="Descrição")),
                (
                    "total_numbers",
                    models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Quantidade total de números"),
                ),
                (
                    "price_per_number",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[MinValueValidator(0)],
                        verbose_name="Preço por número",
                    ),
                ),
                (
                    "inviter_bonus_quantity",
                    models.PositiveIntegerField(
                        default=3,
                        help_text="Quantidade de números liberados para quem compartilha após o indicado resgatar.",
                        verbose_name="Números para quem indica",
                    ),
                ),
                (
                    "invitee_bonus_quantity",
                    models.PositiveIntegerField(
                        default=1,
                        help_text="Quantidade de números liberados para quem recebe o link e resgata.",
                        verbose_name="Números para quem é indicado",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Rascunho"), ("active", "Ativa"), ("archived", "Arquivada")],
                        default="draft",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "allow_random_numbers",
                    models.BooleanField(
                        default=True,
                        help_text="Define se a compra/resgate gera números aleatórios automaticamente.",
                        verbose_name="Números aleatórios",
                    ),
                ),
                ("starts_at", models.DateTimeField(blank=True, null=True, verbose_name="Início")),
                ("ends_at", models.DateTimeField(blank=True, null=True, verbose_name="Término")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Atualizado em")),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="raffles",
                        to="tenants.tenant",
                        verbose_name="Empresa",
                    ),
                ),
            ],
            options={
                "verbose_name": "Rifa",
                "verbose_name_plural": "Rifas",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="RaffleOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(verbose_name="Quantidade de números")),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[MinValueValidator(0)],
                        verbose_name="Valor total",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendente"),
                            ("paid", "Pago"),
                            ("canceled", "Cancelado"),
                            ("expired", "Expirado"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Status do pagamento",
                    ),
                ),
                (
                    "payment_method",
                    models.CharField(
                        choices=[("pix", "Pix"), ("card", "Cartão")],
                        default="pix",
                        max_length=10,
                        verbose_name="Meio de pagamento",
                    ),
                ),
                (
                    "payment_reference",
                    models.CharField(
                        blank=True,
                        help_text="Identificador do PSP/gateway (charge_id, transaction_id, etc).",
                        max_length=120,
                        verbose_name="Referência externa",
                    ),
                ),
                ("pix_qr_code", models.TextField(blank=True, verbose_name="Payload Pix")),
                ("pix_expires_at", models.DateTimeField(blank=True, null=True, verbose_name="Expira em")),
                ("metadata", models.JSONField(blank=True, default=dict, verbose_name="Metadados")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Atualizado em")),
                ("paid_at", models.DateTimeField(blank=True, null=True, verbose_name="Pago em")),
                ("canceled_at", models.DateTimeField(blank=True, null=True, verbose_name="Cancelado em")),
                (
                    "raffle",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="orders",
                        to="raffles.raffle",
                        verbose_name="Rifa",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="raffle_orders",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Participante",
                    ),
                ),
            ],
            options={
                "verbose_name": "Pedido da rifa",
                "verbose_name_plural": "Pedidos da rifa",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="ReferralInvitation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "code",
                    models.CharField(blank=True, default="", max_length=32, unique=True, verbose_name="Código do convite"),
                ),
                ("invitee_email", models.EmailField(blank=True, max_length=254, verbose_name="E-mail do indicado")),
                ("invitee_phone", models.CharField(blank=True, max_length=32, verbose_name="Telefone do indicado")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendente"),
                            ("visited", "Visitado"),
                            ("redeemed", "Resgatado"),
                            ("expired", "Expirado"),
                            ("canceled", "Cancelado"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                ("clicks", models.PositiveIntegerField(default=0, verbose_name="Cliques no link")),
                ("last_clicked_at", models.DateTimeField(blank=True, null=True, verbose_name="Último clique")),
                ("redeemed_at", models.DateTimeField(blank=True, null=True, verbose_name="Resgatado em")),
                (
                    "inviter_bonus_allocated",
                    models.BooleanField(default=False, verbose_name="Bônus entregue ao indicador"),
                ),
                ("metadata", models.JSONField(blank=True, default=dict, verbose_name="Metadados")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                ("expires_at", models.DateTimeField(blank=True, null=True, verbose_name="Expira em")),
                (
                    "invitee",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="raffle_referrals_received",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Quem foi indicado",
                    ),
                ),
                (
                    "inviter",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="raffle_referrals_sent",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Quem convidou",
                    ),
                ),
                (
                    "raffle",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="referrals",
                        to="raffles.raffle",
                        verbose_name="Rifa",
                    ),
                ),
            ],
            options={
                "verbose_name": "Convite de indicação",
                "verbose_name_plural": "Convites de indicação",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="RaffleTicketAllocation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.PositiveIntegerField(verbose_name="Número")),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("purchase", "Compra"),
                            ("referral_inviter", "Indicação - quem convidou"),
                            ("referral_invitee", "Indicação - convidado"),
                            ("manual", "Manual"),
                        ],
                        default="purchase",
                        max_length=32,
                        verbose_name="Origem",
                    ),
                ),
                ("allocated_at", models.DateTimeField(auto_now_add=True, verbose_name="Alocado em")),
                ("metadata", models.JSONField(blank=True, default=dict, verbose_name="Metadados")),
                (
                    "order",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="ticket_allocations",
                        to="raffles.raffleorder",
                        verbose_name="Pedido",
                    ),
                ),
                (
                    "raffle",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="ticket_allocations",
                        to="raffles.raffle",
                        verbose_name="Rifa",
                    ),
                ),
                (
                    "referral",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="ticket_allocations",
                        to="raffles.referralinvitation",
                        verbose_name="Convite",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="raffle_ticket_allocations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Participante",
                    ),
                ),
            ],
            options={
                "verbose_name": "Número da rifa",
                "verbose_name_plural": "Números da rifa",
                "ordering": ("raffle", "number"),
            },
        ),
        migrations.AlterUniqueTogether(
            name="raffleticketallocation",
            unique_together={("raffle", "number")},
        ),
    ]

