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
    
    Tenta servir arquivo estático primeiro, depois retorna index.html
    para deixar React Router lidar com as rotas
    """
    from django.http import FileResponse
    import os
    
    # Tenta arquivo estático em várias localizações
    possible_paths = [
        BASE_DIR / 'frontend' / 'dist' / path,  # Build do Vite
        BASE_DIR / 'frontend' / 'public' / path,  # Arquivos públicos
        BASE_DIR / 'frontend' / 'src' / path,  # Desenvolvimento
        BASE_DIR / 'frontend' / 'dist' / 'index.html',  # Fallback SPA
        BASE_DIR / 'frontend' / 'index.html',  # Fallback SPA alt
    ]
    
    for file_path in possible_paths:
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'))
    
    # Se nada encontrado, retorna 404
    from django.http import Http404
    raise Http404(f"Arquivo não encontrado: {path}")
