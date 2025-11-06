from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from raffles.models import Raffle, RaffleOrder, RaffleTicketAllocation, ReferralInvitation
from raffles.services import RaffleSoldOutError


class RaffleSerializer(serializers.ModelSerializer):
    numbers_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Raffle
        fields = [
            "id",
            "tenant",
            "name",
            "slug",
            "description",
            "total_numbers",
            "price_per_number",
            "inviter_bonus_quantity",
            "invitee_bonus_quantity",
            "status",
            "allow_random_numbers",
            "numbers_available",
            "starts_at",
            "ends_at",
        ]
        read_only_fields = [
            "tenant",
            "numbers_available",
        ]


class RaffleOrderSerializer(serializers.ModelSerializer):
    raffle_id = serializers.PrimaryKeyRelatedField(
        source="raffle",
        queryset=Raffle.objects.all(),
        write_only=True,
    )
    numbers = serializers.SerializerMethodField()

    class Meta:
        model = RaffleOrder
        read_only_fields = [
            "status",
            "amount",
            "payment_reference",
            "pix_qr_code",
            "pix_expires_at",
            "metadata",
            "created_at",
            "paid_at",
        ]
        fields = [
            "id",
            "raffle_id",
            "quantity",
            "amount",
            "status",
            "payment_method",
            "payment_reference",
            "pix_qr_code",
            "pix_expires_at",
            "numbers",
            "created_at",
            "paid_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tenant = self.context.get("tenant")
        if tenant:
            self.fields["raffle_id"].queryset = Raffle.objects.filter(tenant=tenant, status=Raffle.Status.ACTIVE)

    def validate(self, attrs):
        raffle: Raffle = attrs["raffle"]
        quantity = attrs["quantity"]
        if quantity <= 0:
            raise serializers.ValidationError({"quantity": "Informe ao menos 1 número."})
        if quantity > raffle.numbers_available:
            raise serializers.ValidationError({"quantity": "Números insuficientes disponíveis para a rifa."})
        return attrs

    def create(self, validated_data):
        raffle: Raffle = validated_data["raffle"]
        quantity: int = validated_data["quantity"]
        user = self.context["request"].user
        amount = (raffle.price_per_number or Decimal("0")) * quantity

        order = RaffleOrder.objects.create(
            raffle=raffle,
            user=user,
            quantity=quantity,
            amount=amount,
            payment_method=validated_data.get("payment_method") or RaffleOrder.PaymentMethod.PIX,
        )
        return order

    def get_numbers(self, instance: RaffleOrder):
        return sorted(instance.ticket_allocations.values_list("number", flat=True))


class ReferralInvitationSerializer(serializers.ModelSerializer):
    raffle_id = serializers.PrimaryKeyRelatedField(
        source="raffle",
        queryset=Raffle.objects.all(),
        write_only=True,
    )

    class Meta:
        model = ReferralInvitation
        read_only_fields = [
            "code",
            "status",
            "clicks",
            "last_clicked_at",
            "redeemed_at",
            "inviter_bonus_allocated",
        ]
        fields = [
            "id",
            "raffle_id",
            "code",
            "status",
            "invitee_email",
            "invitee_phone",
            "clicks",
            "last_clicked_at",
            "redeemed_at",
            "inviter_bonus_allocated",
            "expires_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tenant = self.context.get("tenant")
        if tenant:
            self.fields["raffle_id"].queryset = Raffle.objects.filter(tenant=tenant, status=Raffle.Status.ACTIVE)

    def create(self, validated_data):
        user = self.context["request"].user
        return ReferralInvitation.objects.create(inviter=user, **validated_data)


class ReferralRedeemSerializer(serializers.Serializer):
    force = serializers.BooleanField(required=False, default=False)

    def save(self, **kwargs):
        referral: ReferralInvitation = self.context["referral"]
        request = self.context["request"]

        invitee = request.user
        if not invitee.is_authenticated:
            raise serializers.ValidationError("É necessário entrar na conta para resgatar.")

        if referral.status == ReferralInvitation.Status.REDEEMED and referral.invitee_id == invitee.id:
            return {"status": referral.status}
        if referral.status == ReferralInvitation.Status.REDEEMED:
            raise serializers.ValidationError("Este convite já foi resgatado por outra pessoa.")

        referral.mark_redeemed(invitee)
        try:
            inviter_allocations, invitee_allocations = RaffleTicketAllocation.allocate_referral_bonus(referral)
        except RaffleSoldOutError as exc:
            raise serializers.ValidationError(str(exc)) from exc

        return {
            "status": referral.status,
            "inviter_numbers": [alloc.number for alloc in inviter_allocations],
            "invitee_numbers": [alloc.number for alloc in invitee_allocations],
        }

