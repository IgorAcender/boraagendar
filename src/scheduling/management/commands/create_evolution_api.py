"""
Django management command para criar Evolution API
"""
from django.core.management.base import BaseCommand
from scheduling.models import EvolutionAPI
from django.conf import settings


class Command(BaseCommand):
    help = 'Cria uma Evolution API padrão no banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--instance-id',
            type=str,
            default='default',
            help='ID da instância Evolution'
        )
        parser.add_argument(
            '--api-url',
            type=str,
            default=None,
            help='URL da API Evolution'
        )
        parser.add_argument(
            '--api-key',
            type=str,
            default='temp-key',
            help='Chave da API'
        )

    def handle(self, *args, **options):
        instance_id = options['instance_id']
        api_url = options['api_url'] or getattr(settings, 'EVOLUTION_API_URL', 'http://localhost:8080/api')
        api_key = options['api_key']

        # Verificar se já existe
        existing = EvolutionAPI.objects.filter(instance_id=instance_id).first()
        if existing:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Evolution API "{instance_id}" já existe!')
            )
            return

        # Criar nova
        evo = EvolutionAPI.objects.create(
            instance_id=instance_id,
            api_url=api_url,
            api_key=api_key,
            is_active=True,
            capacity=10,
            priority=1
        )

        self.stdout.write(
            self.style.SUCCESS(f'✅ Evolution API criada com sucesso!')
        )
        self.stdout.write(f'   ID: {evo.id}')
        self.stdout.write(f'   Instance: {evo.instance_id}')
        self.stdout.write(f'   URL: {evo.api_url}')
        self.stdout.write(f'   Ativa: {evo.is_active}')
