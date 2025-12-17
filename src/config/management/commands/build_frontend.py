from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import subprocess
import shutil
import os


class Command(BaseCommand):
    help = 'Compilar frontend React e copiar para Django static'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-install',
            action='store_true',
            help='Não instala dependências npm',
        )
        parser.add_argument(
            '--dev',
            action='store_true',
            help='Build para desenvolvimento',
        )

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR).parent
        frontend_dir = base_dir / 'frontend'
        static_dir = base_dir / 'src' / 'staticfiles' / 'dist'

        self.stdout.write(
            self.style.SUCCESS('═' * 60)
        )
        self.stdout.write(
            self.style.SUCCESS('🔨 Compilando Frontend React para Django')
        )
        self.stdout.write(
            self.style.SUCCESS('═' * 60)
        )

        # 1. Verificar Node.js
        if not shutil.which('node'):
            self.stdout.write(
                self.style.ERROR('❌ Node.js não encontrado!')
            )
            self.stdout.write(
                self.style.WARNING('📥 Instale de: https://nodejs.org/')
            )
            return

        self.stdout.write('✅ Node.js encontrado')

        # 2. Ir para frontend
        os.chdir(frontend_dir)

        # 3. npm install (se necessário)
        if not options['no_install']:
            self.stdout.write('📦 Instalando dependências npm...')
            result = subprocess.run(['npm', 'install'], capture_output=True)
            if result.returncode != 0:
                self.stdout.write(
                    self.style.ERROR('❌ Erro ao instalar dependências')
                )
                self.stdout.write(result.stderr.decode())
                return

        # 4. npm run build
        self.stdout.write('🏗️  Compilando assets...')
        build_cmd = 'npm run build'
        if options['dev']:
            build_cmd = 'npm run dev'
        
        result = subprocess.run(build_cmd.split(), capture_output=True)
        if result.returncode != 0:
            self.stdout.write(
                self.style.ERROR('❌ Erro ao compilar')
            )
            self.stdout.write(result.stderr.decode())
            return

        # 5. Copiar para Django
        self.stdout.write('📁 Copiando para Django static...')
        dist_dir = frontend_dir / 'dist'
        
        if dist_dir.exists():
            static_dir.parent.mkdir(parents=True, exist_ok=True)
            if static_dir.exists():
                shutil.rmtree(static_dir)
            shutil.copytree(dist_dir, static_dir)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Build copiado para: {static_dir}')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Diretório dist não encontrado!')
            )
            return

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('═' * 60)
        )
        self.stdout.write(
            self.style.SUCCESS('✅ Build Completo!')
        )
        self.stdout.write(
            self.style.SUCCESS('═' * 60)
        )
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('🚀 Próximos passos:')
        )
        self.stdout.write('  1. Inicie o servidor Django:')
        self.stdout.write(
            self.style.WARNING('     python manage.py runserver')
        )
        self.stdout.write('')
        self.stdout.write('  2. Abra no navegador:')
        self.stdout.write(
            self.style.WARNING('     http://localhost:8000/app')
        )
