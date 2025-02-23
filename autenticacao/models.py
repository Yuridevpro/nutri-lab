from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class Ativacao(models.Model):
    token = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ativo = models.BooleanField(default=False)
    token_expiration = models.DateTimeField(default=timezone.now() + timedelta(hours=24))  # Token expira em 24h

    def __str__(self):
        return self.user.username

    def is_token_expired(self):
        return timezone.now() > self.token_expiration


class ResetSenha(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reset_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_token_valid(self):
        expiration_time = self.created_at + timedelta(hours=24)
        return timezone.now() < expiration_time

    def __str__(self):
        return f'ResetSenha para {self.user.username}'
