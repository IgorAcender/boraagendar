"""
Configuração para servir React SPA através do Django
"""
from pathlib import Path
from django.views.generic import TemplateView
from django.urls import re_path
from django.views.static import serve
from django.conf import settings

# Caminho base - aponta para /src (onde manage.py está)
BASE_DIR = Path(__file__).resolve().parent.parent

# URL patterns para SPA
def get_spa_urls():
    """
    Retorna URLs para servir React SPA
    
    A estrutura esperada é:
    - /frontend/dist/index.html (após build do Vite)
    ou
    - /frontend/src/index.html (durante desenvolvimento)
    """
    
    spa_patterns = [
        # API endpoints - mantém a prioridade
        re_path(r'^api/', None),  # Será resolvido em urls.py
        
        # Rotas do React SPA - serve o index.html
        re_path(r'^$', serve_spa, {'path': 'index.html'}),
        re_path(r'^(?!api|admin|static).+$', serve_spa, {'path': 'index.html'}),
    ]
    
    return spa_patterns


def serve_spa(request, path='index.html'):
    """
    Serve arquivos estáticos do React SPA
    
    O React é buildado para: /src/static/dist/
    Django serve static files automaticamente em: /static/
    
    Esta função serve o index.html para rotear via React Router
    """
    from django.http import FileResponse
    from django.shortcuts import render
    import os
    
    print(f"🔍 serve_spa called with path: {path}")
    print(f"📁 BASE_DIR: {BASE_DIR}")
    
    # Se a rota pedir especificamente pelo Balasis (ex: /app/balasis/*), servir o index do Balasis
    try:
        req_path = request.path
    except Exception:
        req_path = ''

    # Se a rota pedir pelo app Balasis (ex: /app, /app/*, /app/balasis/*), servir o index do Balasis
    # Isso faz com que a interface Balasis seja a aplicação carregada no path /app
    if req_path.startswith('/app') or req_path.startswith('/app/balasis') or req_path.startswith('/balasis'):
        path = 'balasis/index.html'

    # Tenta arquivo estático em várias localizações (ordem de prioridade)
    possible_paths = [
        BASE_DIR / 'static' / 'dist' / path,  # Build do Vite para Django static
        BASE_DIR / 'frontend' / 'dist' / path,  # Build do Vite (fallback)
        BASE_DIR / 'static' / 'dist' / 'index.html',  # Fallback SPA (index)
        BASE_DIR / 'frontend' / 'dist' / 'index.html',  # Fallback SPA alt
    ]
    
    for file_path in possible_paths:
        print(f"  Tentando: {file_path}")
        if os.path.exists(file_path):
            print(f"  ✅ Encontrado: {file_path}")
            try:
                return FileResponse(open(file_path, 'rb'), content_type='text/html')
            except Exception as e:
                print(f"  ❌ Erro ao servir: {e}")
                pass
    
    print(f"  ❌ Nenhum arquivo encontrado, usando spa.html template")
    # Se nada encontrado, retorna o SPA template
    return render(request, 'spa.html')
