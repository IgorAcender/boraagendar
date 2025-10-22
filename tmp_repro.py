from django.contrib.auth import get_user_model
from django.test import Client

from tenants.models import Tenant, TenantMembership
from scheduling.models import Professional


User = get_user_model()

user = User.objects.create_user(email="owner@example.com", password="pass123")
tenant = Tenant.objects.create(name="Salon", slug="salon")
TenantMembership.objects.create(tenant=tenant, user=user, role=TenantMembership.Role.OWNER)

client = Client()
logged = client.login(email="owner@example.com", password="pass123")
print("logged", logged)

response = client.post(
    "/dashboard/profissionais/",
    {
        "display_name": "Prof Test",
        "bio": "",
        "color": "#123456",
        "is_active": "on",
    },
)
print("response status", response.status_code)
print("redirect", response.headers.get("Location"))
print("professionals", Professional.objects.count())
