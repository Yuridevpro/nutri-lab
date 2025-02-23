# views.py
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth
from django.conf import settings
from .models import Ativacao, ResetSenha
from hashlib import sha256
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from .utils import password_is_valid, email_html
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from datetime import timedelta
import re


def cadastro(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        # username = request.POST.get('usuario') #remova essa linha
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not password_is_valid(request, senha, confirmar_senha):
            return redirect('/auth/cadastro')

        # Validar se o email já existe
        if User.objects.filter(email=email).exists():
            user_inativo = User.objects.filter(email=email, is_active=False).first()
            if user_inativo:
                # Reenviar email de ativação
                token = sha256(f"{user_inativo.username} {email}".encode()).hexdigest()
                ativacao, created = Ativacao.objects.get_or_create(user=user_inativo)
                ativacao.token = token
                ativacao.token_expiration = timezone.now() + timedelta(hours=24)
                ativacao.save()

                # Gerar URL de ativação usando reverse
                url_ativacao = request.build_absolute_uri(reverse('ativar_conta', kwargs={'token': token}))

                # Carregar o template de e-mail
                template = render_to_string('emails/cadastro_confirmado.html', {'username': user_inativo.username, 'link_ativacao': url_ativacao})

                # Enviar o e-mail
                email_message = EmailMessage(
                    'Reativação de Conta',
                    template,
                    settings.DEFAULT_FROM_EMAIL,  # Remetente
                    [email],  # Destinatários
                )
                email_message.content_subtype = "html"  # Definir o tipo de conteúdo como HTML
                email_message.send()

                messages.add_message(request, constants.SUCCESS, 'Um novo link de ativação foi enviado para seu e-mail.')
                return redirect('/auth/logar')
            else:
                messages.add_message(request, constants.ERROR, 'Este e-mail já está cadastrado.')
                return redirect('/auth/cadastro')

        try:
            #username = email.split('@')[0]  # Use o nome antes do @ como username
            username = email  # Defina o email como username
            user = User.objects.create_user(username=username, email=email, password=senha, is_active=False)
            user.save()

            token = sha256(f"{username} {email}".encode()).hexdigest()
            ativacao = Ativacao(token=token, user=user)
            ativacao.save()

            # Gerar URL de ativação usando reverse
            url_ativacao = request.build_absolute_uri(reverse('ativar_conta', kwargs={'token': token}))

            # Carregar o template de e-mail
            template = render_to_string('emails/cadastro_confirmado.html', {'username': username, 'link_ativacao': url_ativacao})

            # Enviar o e-mail
            email_message = EmailMessage(
                'Cadastro Confirmado',
                template,
                settings.DEFAULT_FROM_EMAIL,  # Remetente
                [email],  # Destinatários
            )
            email_message.content_subtype = "html"  # Definir o tipo de conteúdo como HTML
            email_message.send()

            messages.add_message(request, constants.SUCCESS, 'Cadastro realizado com sucesso! Verifique seu e-mail para ativar a conta.')
            return redirect('/auth/logar')
        except Exception as e:  # Capturar a exceção para depuração
            print(f"Erro ao cadastrar: {e}")  # Imprime o erro no console (útil para depurar)
            messages.add_message(request, constants.ERROR, 'Erro interno sistema!')
            return redirect('/auth/cadastro')


def logar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'logar.html')
    elif request.method == "POST":
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            user = User.objects.get(email=email) #login pelo email
        except User.DoesNotExist:
            messages.add_message(request, constants.ERROR, 'Email ou senha inválidos')
            return render(request, 'logar.html')

        usuario = auth.authenticate(request, username=user.username, password=senha)

        if not usuario:
            messages.add_message(request, constants.ERROR, 'Email ou senha inválidos')
            return render(request, 'logar.html')
        else:
            auth.login(request, usuario)
            return redirect('/pacientes')


def sair(request):
    auth.logout(request)
    return redirect('/auth/logar')


def ativar_conta(request, token):
    ativacao = get_object_or_404(Ativacao, token=token) # apenas arrumei aqui, pois estava token e nao ativacao
    if ativacao.ativo:
        messages.add_message(request, constants.WARNING, 'Esse token já foi usado')
        return redirect('/auth/logar')

    user = User.objects.get(username=ativacao.user.username)
    user.is_active = True
    user.save()

    ativacao.ativo = True
    ativacao.save()

    messages.add_message(request, constants.SUCCESS, 'Conta ativa com sucesso')
    return redirect('/auth/logar')


def esqueceu_senha(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            # Salvar o token de reset na tabela ResetSenha
            reset_senha = ResetSenha.objects.create(user=user, reset_token=token)
            reset_senha.save()

            # Construir link de reset
            reset_link = request.build_absolute_uri(reverse('criar_senha', kwargs={'uidb64': uidb64, 'token': token}))

            # Enviar e-mail com o link de reset
            subject = "Redefinir sua senha"
            message = render_to_string('emails/email_reset_senha.html', {
                'user': user.username,
                'reset_link': reset_link,
            })
            email_message = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            email_message.content_subtype = "html"
            email_message.send()

            messages.add_message(request, constants.SUCCESS, "Verifique seu e-mail para redefinir sua senha.")
            return redirect('/auth/logar')

        except User.DoesNotExist:
            messages.add_message(request, constants.ERROR, "Este e-mail não está registrado.")
            return redirect('/auth/esqueceu_senha')

    return render(request, 'esqueceu_senha.html')


def criar_senha(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)

        reset_senha = ResetSenha.objects.get(user=user)
        if reset_senha.reset_token != token or not reset_senha.is_token_valid():
            messages.add_message(request, constants.ERROR, "O token de reset é inválido ou expirou.")
            return redirect('/auth/logar')

        if request.method == "POST":
            nova_senha = request.POST.get('senha')
            confirmar_senha = request.POST.get('confirmar_senha')

            if nova_senha == confirmar_senha:
                user.set_password(nova_senha)
                user.save()

                # Deletar o token de reset após a redefinição
                reset_senha.delete()

                messages.add_message(request, constants.SUCCESS, "Sua senha foi redefinida com sucesso. Faça login.")
                return redirect('/auth/logar')


            else:
                messages.add_message(request, constants.ERROR, "As senhas não coincidem.")
                return redirect('criar_senha', uidb64=uidb64, token=token)

    except (User.DoesNotExist, ResetSenha.DoesNotExist):
        messages.add_message(request, constants.ERROR, "Token inválido ou expirado.")
        return redirect('/auth/logar')

    return render(request, 'criar_senha.html', {'uidb64': uidb64, 'token': token})