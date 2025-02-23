# Generated by Django 5.1.3 on 2025-02-22 16:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0003_refeicao_opcao'),
    ]

    operations = [
        migrations.AddField(
            model_name='pacientes',
            name='habitos_alimentares',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pacientes',
            name='historico_medico',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pacientes',
            name='metas',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pacientes',
            name='nivel_atividade_fisica',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='Laudo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('nome', models.CharField(max_length=100)),
                ('arquivo', models.FileField(upload_to='laudos/')),
                ('descricao', models.TextField(blank=True, null=True)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plataforma.pacientes')),
            ],
        ),
        migrations.CreateModel(
            name='PlanoAlimentar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_criacao', models.DateField(auto_now_add=True)),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plataforma.pacientes')),
            ],
        ),
    ]
