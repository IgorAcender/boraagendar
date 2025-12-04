#!/usr/bin/env python
import os
import sys
import django

# Adicionar o path do src
sys.path.insert(0, '/Users/user/Desktop/Programação/boraagendar/src')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from scheduling.models import Professional
from scheduling.forms import ProfessionalUpdateForm
from django.test import RequestFactory

# Buscar um profissional existente
professional = Professional.objects.first()

if professional:
    print(f'✓ Profissional encontrado: {professional.display_name}')
    print(f'  - Bio: {repr(professional.bio)}')
    print(f'  - Bio Type: {type(professional.bio).__name__}')
    print(f'  - Tenant: {professional.tenant.name}')
    
    # Simular dados POST (sem modificações)
    post_data = {
        'display_name': professional.display_name,
        'photo': '',
        'bio': professional.bio or '',
        'color': professional.color,
        'is_active': professional.is_active,
        'allow_auto_assign': professional.allow_auto_assign,
        'user_full_name': professional.user.get_full_name() if professional.user else '',
        'user_email': professional.user.email if professional.user else '',
        'user_phone_number': professional.user.phone_number if professional.user else '',
        'user_password': '',
        'user': professional.user.pk if professional.user else '',
    }
    
    print(f'\n✓ Dados POST preparados:')
    for key, value in post_data.items():
        print(f'  - {key}: {repr(value)}')
    
    # Tentar criar o formulário
    print(f'\n→ Criando formulário...')
    try:
        form = ProfessionalUpdateForm(
            data=post_data,
            instance=professional,
            tenant=professional.tenant
        )
        print(f'✓ Formulário criado com sucesso')
        
        # Validar o formulário
        print(f'→ Validando formulário...')
        is_valid = form.is_valid()
        print(f'✓ Validação: {is_valid}')
        
        if not is_valid:
            print(f'✗ Erros de validação:')
            for field, errors in form.errors.items():
                print(f'  - {field}: {errors}')
        else:
            # Tentar salvar
            print(f'→ Salvando formulário...')
            saved = form.save()
            print(f'✓ Formulário salvo com sucesso!')
            print(f'  - ID: {saved.pk}')
            print(f'  - Bio: {repr(saved.bio)}')
    
    except Exception as e:
        print(f'✗ Erro: {e}')
        import traceback
        traceback.print_exc()
else:
    print('✗ Nenhum profissional encontrado no banco de dados')
