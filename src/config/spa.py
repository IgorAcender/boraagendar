"""
Configuração para servir React SPA através do Django
"""
from pathlib import Path
from django.views.generic import TemplateView
from django.urls import re_path
from django.views.static import serve
from django.conf import settings

# Caminho base
BASE_DIR = Path(__file__).resolve().parent.parent.parent

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
    
    # Tenta arquivo estático em várias localizações (ordem de prioridade)
    possible_paths = [
        BASE_DIR / 'static' / 'dist' / path,  # Build do Vite para Django static
        BASE_DIR / 'frontend' / 'dist' / path,  # Build do Vite (fallback)
        BASE_DIR / 'frontend' / 'public' / path,  # Arquivos públicos
        BASE_DIR / 'static' / 'dist' / 'index.html',  # Fallback SPA (index)
        BASE_DIR / 'frontend' / 'dist' / 'index.html',  # Fallback SPA alt
    ]
    
    for file_path in possible_paths:
        if os.path.exists(file_path):
            try:
                return FileResponse(open(file_path, 'rb'))
            except Exception:
                pass
    
    # Se nada encontrado, retorna o SPA template
    return render(request, 'spa.html')
