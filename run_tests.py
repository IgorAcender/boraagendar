import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import sys
sys.path.insert(0, '/Users/user/Desktop/Programação/boraagendar/src')
django.setup()

# Rodar testes
from django.core.management import call_command
call_command('test', 'scheduling.tests.test_forms', '-v', '2')
