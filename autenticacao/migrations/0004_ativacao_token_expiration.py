# Generated by Django 5.1.3 on 2025-02-22 18:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autenticacao', '0003_alter_ativacao_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='ativacao',
            name='token_expiration',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 23, 18, 41, 5, 667304, tzinfo=datetime.timezone.utc)),
        ),
    ]
