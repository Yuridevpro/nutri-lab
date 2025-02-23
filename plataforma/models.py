from django.db import models
from django.contrib.auth.models import User

class Pacientes(models.Model):
    choices_sexo = (('F', 'Feminino'), ('M', 'Maculino'))
    nome = models.CharField(max_length=50)
    sexo = models.CharField(max_length=1, choices=choices_sexo)
    idade = models.IntegerField()
    email = models.EmailField()
    telefone = models.CharField(max_length=19)
    nutri = models.ForeignKey(User, on_delete=models.CASCADE)

    # Novos campos
    historico_medico = models.TextField(blank=True, null=True)  # Doenças, alergias, etc.
    habitos_alimentares = models.TextField(blank=True, null=True)
    nivel_atividade_fisica = models.CharField(max_length=50, blank=True, null=True)
    metas = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

class Laudo(models.Model):
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    data = models.DateTimeField(auto_now_add=True)  # Data de criação automática
    nome = models.CharField(max_length=100)  # Nome do laudo (ex: "Exame de Sangue")
    arquivo = models.FileField(upload_to='laudos/')  # Armazena o arquivo (PDF, imagem, etc.)
    descricao = models.TextField(blank=True, null=True)  # Descrição opcional

    def __str__(self):
        return f"Laudo de {self.paciente.nome} - {self.nome}"


class PlanoAlimentar(models.Model):  # Novo modelo para planos alimentares
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    data_criacao = models.DateField(auto_now_add=True)
    nome = models.CharField(max_length=100)  # Ex: "Plano para Ganho de Massa"
    descricao = models.TextField(blank=True, null=True)  # Descrição opcional

    def __str__(self):
        return f"Plano de {self.paciente.nome} - {self.nome}"


class DadosPaciente(models.Model): #Mantendo existente
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    data = models.DateTimeField()
    peso = models.IntegerField()
    altura = models.IntegerField()
    percentual_gordura = models.IntegerField()
    percentual_musculo = models.IntegerField()
    colesterol_hdl = models.IntegerField()
    colesterol_ldl = models.IntegerField()
    colesterol_total = models.IntegerField()
    trigliceridios = models.IntegerField()

    def __str__(self):
        return f"Paciente({self.paciente.nome}, {self.peso})"

class Refeicao(models.Model): #Mantendo existente
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=50)
    horario = models.TimeField()
    carboidratos = models.IntegerField()
    proteinas = models.IntegerField()
    gorduras = models.IntegerField()

    def __str__(self):
        return self.titulo

class Opcao(models.Model): #Mantendo existente
    refeicao = models.ForeignKey(Refeicao, on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to="opcao")
    descricao = models.TextField()

    def __str__(self):
        return self.descricao