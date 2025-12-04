#!/usr/bin/env python3
import os

files = [
    '/Users/user/Desktop/Programação/boraagendar/src/templates/scheduling/public/base_public.html',
    '/Users/user/Desktop/Programação/boraagendar/src/templates/scheduling/public/booking_start.html',
    '/Users/user/Desktop/Programação/boraagendar/src/templates/scheduling/public/booking_confirm.html',
]

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituições para tornar todos os textos dinâmicos
        content = content.replace('color: white;', 'color: var(--text-light);')
        content = content.replace("color: white;", "color: var(--text-light);")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Processado: {file_path}")
    else:
        print(f"❌ Arquivo não encontrado: {file_path}")

print("\n✨ Todas as cores brancas foram convertidas para var(--text-light)!")
