from rest_framework import serializers

from scheduling.models import Booking, Professional, Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "duration_minutes",
            "price",
            "is_active",
        ]


class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = [
            "id",
            "display_name",
            "bio",
            "color",
            "is_active",
        ]


class BookingSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tenant = self.context.get("tenant")
        if tenant:
            self.fields["service_id"].queryset = Service.objects.filter(tenant=tenant)
            self.fields["professional_id"].queryset = Professional.objects.filter(tenant=tenant)

    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        source="service",
        queryset=Service.objects.all(),
        write_only=True,
    )
    professional = ProfessionalSerializer(read_only=True)
    professional_id = serializers.PrimaryKeyRelatedField(
        source="professional",
        queryset=Professional.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "service",
            "service_id",
            "professional",
            "professional_id",
            "customer_name",
            "customer_phone",
            "customer_email",
            "scheduled_for",
            "duration_minutes",
            "price",
            "status",
            "notes",
        ]
