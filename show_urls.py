import os
import django
from django.urls import get_resolver

# Configurar o Django manualmente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutri_lab.settings')  # Certifique-se de que 'nutri_lab' está correto
django.setup()

def list_urls(patterns=None, prefix=""):
    if patterns is None:
        patterns = get_resolver().url_patterns  # Obtém todas as URLs do projeto

    for pattern in patterns:
        try:
            route = prefix + str(pattern.pattern)  # Constrói a URL completa
            if hasattr(pattern, "url_patterns"):  # Se for um include(), percorre recursivamente
                list_urls(pattern.url_patterns, prefix=route)
            else:
                print(f"{route} → {pattern.callback.__name__}")  # Exibe a URL e a função correspondente
        except AttributeError:
            print(f"{route} → (Sem nome de função)")

list_urls()
