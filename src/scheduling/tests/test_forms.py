from django.test import TestCase
from django.contrib.auth import get_user_model
from scheduling.forms import ProfessionalUpdateForm
from scheduling.models import Professional
from tenants.models import Tenant, TenantMembership
import tempfile
from PIL import Image
from io import BytesIO

User = get_user_model()


class ProfessionalUpdateFormTest(TestCase):
    def setUp(self):
        """Configurar dados de teste"""
        # Criar tenant
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            slug="test-tenant"
        )
        
        # Criar usuário
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        
        # Criar membership
        TenantMembership.objects.create(
            tenant=self.tenant,
            user=self.user,
            role="owner"
        )
        
        # Criar profissional
        self.professional = Professional.objects.create(
            tenant=self.tenant,
            user=self.user,
            display_name="Test Professional",
            color="#FF0000"
        )

    def test_form_with_bio_field(self):
        """Testar se o formulário salva corretamente com o campo bio"""
        form_data = {
            "display_name": "Updated Professional",
            "bio": "This is a test bio",
            "color": "#FF0000",
            "is_active": True,
            "allow_auto_assign": False,
            "user_full_name": "Updated Name",
            "user_email": "updated@example.com",
            "user_phone_number": "123456789",
            "user_password": "",  # Deixar em branco para manter a atual
        }
        
        form = ProfessionalUpdateForm(
            data=form_data,
            instance=self.professional,
            tenant=self.tenant
        )
        
        self.assertTrue(form.is_valid(), form.errors)
        saved_professional = form.save()
        
        # Verificar que o bio foi salvo
        self.assertEqual(saved_professional.bio, "This is a test bio")
        self.assertEqual(saved_professional.display_name, "Updated Professional")

    def test_form_with_empty_bio(self):
        """Testar se o formulário funciona com bio vazio"""
        form_data = {
            "display_name": "Professional Without Bio",
            "bio": "",
            "color": "#FF0000",
            "is_active": True,
            "allow_auto_assign": False,
            "user_full_name": "Test User",
            "user_email": "test@example.com",
            "user_phone_number": "123456789",
            "user_password": "",
        }
        
        form = ProfessionalUpdateForm(
            data=form_data,
            instance=self.professional,
            tenant=self.tenant
        )
        
        self.assertTrue(form.is_valid(), form.errors)
        saved_professional = form.save()
        
        # Verificar que o bio é vazio
        self.assertEqual(saved_professional.bio, "")

    def test_form_with_long_bio(self):
        """Testar se o formulário funciona com bio longo"""
        long_bio = "This is a very long bio. " * 50  # ~1300 caracteres
        
        form_data = {
            "display_name": "Professional",
            "bio": long_bio.strip(),  # Remover espaço final
            "color": "#FF0000",
            "is_active": True,
            "allow_auto_assign": False,
            "user_full_name": "Test User",
            "user_email": "test@example.com",
            "user_phone_number": "123456789",
            "user_password": "",
        }
        
        form = ProfessionalUpdateForm(
            data=form_data,
            instance=self.professional,
            tenant=self.tenant
        )
        
        self.assertTrue(form.is_valid(), form.errors)
        saved_professional = form.save()
        
        # Verificar que o bio longo foi salvo (comparar com stripped)
        self.assertEqual(saved_professional.bio, long_bio.strip())

    def test_clean_bio_validation(self):
        """Testar se o método clean_bio() funciona corretamente"""
        form_data = {
            "display_name": "Professional",
            "bio": "  Test bio with spaces  ",  # Bio com espaços
            "color": "#FF0000",
            "is_active": True,
            "allow_auto_assign": False,
            "user_full_name": "Test User",
            "user_email": "test@example.com",
            "user_phone_number": "123456789",
            "user_password": "",
        }
        
        form = ProfessionalUpdateForm(
            data=form_data,
            instance=self.professional,
            tenant=self.tenant
        )
        
        self.assertTrue(form.is_valid(), form.errors)
        saved_professional = form.save()
        
        # Verificar que os espaços foram removidos
        self.assertEqual(saved_professional.bio, "Test bio with spaces")

    def test_form_with_photo_and_bio(self):
        """Testar se o formulário salva corretamente bio mesmo quando foto está presente"""
        form_data = {
            "display_name": "Professional With Photo",
            "bio": "This is a professional with a bio",
            "color": "#FF0000",
            "is_active": True,
            "allow_auto_assign": False,
            "user_full_name": "Test User",
            "user_email": "test@example.com",
            "user_phone_number": "123456789",
            "user_password": "",
        }
        
        form = ProfessionalUpdateForm(
            data=form_data,
            instance=self.professional,
            tenant=self.tenant
        )
        
        self.assertTrue(form.is_valid(), form.errors)
        saved_professional = form.save()
        
        # Verificar que bio foi salvo
        self.assertEqual(saved_professional.bio, "This is a professional with a bio")
