from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

from tenants.models import Tenant


class Raffle(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        ACTIVE = "active", "Ativa"
        ARCHIVED = "archived", "Arquivada"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="raffles",
        verbose_name="Empresa",
    )
    name = models.CharField("Nome", max_length=150)
    slug = models.SlugField("Slug", unique=True)
    description = models.TextField("Descrição", blank=True)
    total_numbers = models.PositiveIntegerField(
        "Quantidade total de números",
        validators=[MinValueValidator(1)],
    )
    price_per_number = models.DecimalField(
        "Preço por número",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    inviter_bonus_quantity = models.PositiveIntegerField(
        "Números para quem indica",
        default=3,
        help_text="Quantidade de números liberados para quem compartilha após o indicado resgatar.",
    )
    invitee_bonus_quantity = models.PositiveIntegerField(
        "Números para quem é indicado",
        default=1,
        help_text="Quantidade de números liberados para quem recebe o link e resgata.",
    )
    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    allow_random_numbers = models.BooleanField(
        "Números aleatórios",
        default=True,
        help_text="Define se a compra/resgate gera números aleatórios automaticamente.",
    )
    starts_at = models.DateTimeField("Início", null=True, blank=True)
    ends_at = models.DateTimeField("Término", null=True, blank=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Rifa"
        verbose_name_plural = "Rifas"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.name

    def get_next_reference(self) -> str:
        """Gera um código curto para links de indicação."""
        return uuid.uuid4().hex[:12]

    @property
    def allocated_numbers_count(self) -> int:
        return self.ticket_allocations.count()

    @property
    def numbers_available(self) -> int:
        return max(self.total_numbers - self.allocated_numbers_count, 0)


class RaffleOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        PAID = "paid", "Pago"
        CANCELED = "canceled", "Cancelado"
        EXPIRED = "expired", "Expirado"

    class PaymentMethod(models.TextChoices):
        PIX = "pix", "Pix"
        CARD = "card", "Cartão"

    raffle = models.ForeignKey(
        Raffle,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Rifa",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="raffle_orders",
        verbose_name="Participante",
    )
    quantity = models.PositiveIntegerField("Quantidade de números")
    amount = models.DecimalField(
        "Valor total",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    status = models.CharField(
        "Status do pagamento",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    payment_method = models.CharField(
        "Meio de pagamento",
        max_length=10,
        choices=PaymentMethod.choices,
        default=PaymentMethod.PIX,
    )
    payment_reference = models.CharField(
        "Referência externa",
        max_length=120,
        blank=True,
        help_text="Identificador do PSP/gateway (charge_id, transaction_id, etc).",
    )
    pix_qr_code = models.TextField("Payload Pix", blank=True)
    pix_expires_at = models.DateTimeField("Expira em", null=True, blank=True)
    metadata = models.JSONField("Metadados", default=dict, blank=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)
    paid_at = models.DateTimeField("Pago em", null=True, blank=True)
    canceled_at = models.DateTimeField("Cancelado em", null=True, blank=True)

    class Meta:
        verbose_name = "Pedido da rifa"
        verbose_name_plural = "Pedidos da rifa"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Pedido {self.id} - {self.raffle.name}"

    @property
    def is_paid(self) -> bool:
        return self.status == self.Status.PAID

    def mark_paid(self, *, reference: str | None = None, auto_allocate: bool = True):
        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        if reference:
            self.payment_reference = reference
        self.save(update_fields=["status", "paid_at", "payment_reference", "updated_at"])
        if auto_allocate:
            RaffleTicketAllocation.allocate_for_order(self)


class ReferralInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        VISITED = "visited", "Visitado"
        REDEEMED = "redeemed", "Resgatado"
        EXPIRED = "expired", "Expirado"
        CANCELED = "canceled", "Cancelado"

    raffle = models.ForeignKey(
        Raffle,
        on_delete=models.CASCADE,
        related_name="referrals",
        verbose_name="Rifa",
    )
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="raffle_referrals_sent",
        verbose_name="Quem convidou",
    )
    code = models.CharField(
        "Código do convite",
        max_length=32,
        unique=True,
        default="",
        blank=True,
    )
    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="raffle_referrals_received",
        verbose_name="Quem foi indicado",
        null=True,
        blank=True,
    )
    invitee_email = models.EmailField("E-mail do indicado", blank=True)
    invitee_phone = models.CharField("Telefone do indicado", max_length=32, blank=True)
    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    clicks = models.PositiveIntegerField("Cliques no link", default=0)
    last_clicked_at = models.DateTimeField("Último clique", null=True, blank=True)
    redeemed_at = models.DateTimeField("Resgatado em", null=True, blank=True)
    inviter_bonus_allocated = models.BooleanField("Bônus entregue ao indicador", default=False)
    metadata = models.JSONField("Metadados", default=dict, blank=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    expires_at = models.DateTimeField("Expira em", null=True, blank=True)

    class Meta:
        verbose_name = "Convite de indicação"
        verbose_name_plural = "Convites de indicação"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Convite {self.code or 'sem código'} - {self.raffle.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.raffle.get_next_reference()
        super().save(*args, **kwargs)

    @property
    def is_pending(self) -> bool:
        return self.status in {self.Status.PENDING, self.Status.VISITED}

    def register_visit(self):
        self.clicks = models.F("clicks") + 1
        self.last_clicked_at = timezone.now()
        if self.status == self.Status.PENDING:
            self.status = self.Status.VISITED
        self.save(update_fields=["clicks", "last_clicked_at", "status"])

    def mark_redeemed(self, invitee):
        self.invitee = invitee
        self.redeemed_at = timezone.now()
        self.status = self.Status.REDEEMED
        self.save(update_fields=["invitee", "redeemed_at", "status"])


class RaffleTicketAllocation(models.Model):
    class Source(models.TextChoices):
        PURCHASE = "purchase", "Compra"
        REFERRAL_INVITER = "referral_inviter", "Indicação - quem convidou"
        REFERRAL_INVITEE = "referral_invitee", "Indicação - convidado"
        MANUAL = "manual", "Manual"

    raffle = models.ForeignKey(
        Raffle,
        on_delete=models.CASCADE,
        related_name="ticket_allocations",
        verbose_name="Rifa",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="raffle_ticket_allocations",
        verbose_name="Participante",
    )
    number = models.PositiveIntegerField("Número")
    source = models.CharField(
        "Origem",
        max_length=32,
        choices=Source.choices,
        default=Source.PURCHASE,
    )
    order = models.ForeignKey(
        "RaffleOrder",
        on_delete=models.SET_NULL,
        related_name="ticket_allocations",
        null=True,
        blank=True,
        verbose_name="Pedido",
    )
    referral = models.ForeignKey(
        "ReferralInvitation",
        on_delete=models.SET_NULL,
        related_name="ticket_allocations",
        null=True,
        blank=True,
        verbose_name="Convite",
    )
    allocated_at = models.DateTimeField("Alocado em", auto_now_add=True)
    metadata = models.JSONField("Metadados", default=dict, blank=True)

    class Meta:
        verbose_name = "Número da rifa"
        verbose_name_plural = "Números da rifa"
        unique_together = ("raffle", "number")
        ordering = ("raffle", "number")

    def __str__(self) -> str:
        return f"{self.raffle.name} #{self.number}"

    @classmethod
    def allocate_for_order(cls, order: "RaffleOrder") -> list["RaffleTicketAllocation"]:
        from .services import pick_random_numbers

        if order.quantity <= 0:
            return []

        with transaction.atomic():
            raffle = order.raffle
            numbers = pick_random_numbers(raffle, order.quantity)
            allocations = [
                cls.objects.create(
                    raffle=raffle,
                    user=order.user,
                    number=number,
                    source=cls.Source.PURCHASE,
                    order=order,
                )
                for number in numbers
            ]
        return allocations

    @classmethod
    def allocate_referral_bonus(
        cls, referral: "ReferralInvitation"
    ) -> tuple[list["RaffleTicketAllocation"], list["RaffleTicketAllocation"]]:
        """
        Gera os números gratuitos para o indicado e para quem convidou.

        Retorna uma tupla (indicador, indicado).
        """
        from .services import pick_random_numbers

        raffle = referral.raffle
        if not referral.invitee:
            raise ValueError("Não é possível gerar bônus sem vincular o convidado ao usuário.")

        inviter_qty = raffle.inviter_bonus_quantity
        invitee_qty = raffle.invitee_bonus_quantity

        with transaction.atomic():
            numbers_needed = inviter_qty + invitee_qty
            numbers = pick_random_numbers(raffle, numbers_needed)
            inviter_numbers = numbers[:inviter_qty]
            invitee_numbers = numbers[inviter_qty:]

            inviter_allocations = [
                cls.objects.create(
                    raffle=raffle,
                    user=referral.inviter,
                    number=num,
                    source=cls.Source.REFERRAL_INVITER,
                    referral=referral,
                )
                for num in inviter_numbers
            ]
            invitee_allocations = [
                cls.objects.create(
                    raffle=raffle,
                    user=referral.invitee,
                    number=num,
                    source=cls.Source.REFERRAL_INVITEE,
                    referral=referral,
                )
                for num in invitee_numbers
            ]

            referral.inviter_bonus_allocated = True
            referral.save(update_fields=["inviter_bonus_allocated"])

        return inviter_allocations, invitee_allocations

