from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name="cadastro"),  
    path('logar/', views.logar, name="logar"),    
    path('sair/', views.sair, name="sair"),
    path('ativar_conta/<str:token>/', views.ativar_conta, name='ativar_conta'),
    path('esqueceu_senha/', views.esqueceu_senha, name='esqueceu_senha'),  # Nova URL para "Esqueci a Senha"
    path('criar_senha/<str:uidb64>/<str:token>/', views.criar_senha, name='criar_senha'),  # Nova URL para criar senha
]
