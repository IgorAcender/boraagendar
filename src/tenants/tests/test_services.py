from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase

from tenants.models import Tenant, TenantMembership
from tenants.services import (
    TenantSelectionRequired,
    ensure_membership,
    ensure_membership_for_request,
)

User = get_user_model()


class MembershipServiceTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Studio", slug="studio")
        self.user = User.objects.create_user(email="user1@example.com", password="pass123")
        self.membership = TenantMembership.objects.create(
            tenant=self.tenant,
            user=self.user,
            role=TenantMembership.Role.PROFESSIONAL,
            is_active=True,
        )

    def test_ensure_membership_returns_membership(self):
        resolved = ensure_membership(self.user)
        self.assertEqual(resolved.tenant, self.tenant)
        self.assertEqual(resolved.role, TenantMembership.Role.PROFESSIONAL)

    def test_ensure_membership_checks_roles(self):
        with self.assertRaises(PermissionDenied):
            ensure_membership(self.user, allowed_roles=[TenantMembership.Role.OWNER, TenantMembership.Role.MANAGER])

    def test_ensure_membership_requires_selection_for_multiple(self):
        other_tenant = Tenant.objects.create(name="Studio 2", slug="studio-2")
        TenantMembership.objects.create(
            tenant=other_tenant,
            user=self.user,
            role=TenantMembership.Role.MANAGER,
            is_active=True,
        )
        with self.assertRaises(TenantSelectionRequired):
            ensure_membership(self.user)

    def test_ensure_membership_accepts_explicit_tenant_id(self):
        other_tenant = Tenant.objects.create(name="Studio 2", slug="studio-2")
        TenantMembership.objects.create(
            tenant=other_tenant,
            user=self.user,
            role=TenantMembership.Role.MANAGER,
            is_active=True,
        )
        resolved = ensure_membership(self.user, tenant_id=other_tenant.id)
        self.assertEqual(resolved.tenant, other_tenant)
        self.assertEqual(resolved.role, TenantMembership.Role.MANAGER)

    def test_ensure_membership_for_request_uses_session(self):
        request = RequestFactory().get("/")
        request.user = self.user
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        request.session["active_tenant_id"] = self.tenant.id
        resolved = ensure_membership_for_request(request)
        self.assertEqual(resolved.tenant_id, self.tenant.id)
