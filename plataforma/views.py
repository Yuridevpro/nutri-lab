from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from .models import Pacientes, DadosPaciente, Refeicao, Opcao, Laudo  # Importe Laudo
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

@login_required
def pacientes(request):
    if request.method == 'GET':
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'pacientes.html', {'pacientes': pacientes})
    elif request.method == "POST":
        nome = request.POST.get('nome')
        sexo = request.POST.get('sexo')
        idade = request.POST.get('idade')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        historico_medico = request.POST.get('historico_medico')  # Novos campos
        habitos_alimentares = request.POST.get('habitos_alimentares')
        nivel_atividade_fisica = request.POST.get('nivel_atividade_fisica')
        metas = request.POST.get('metas')

        if (len(nome.strip()) == 0) or (len(sexo.strip()) == 0) or (len(idade.strip()) == 0) or (len(email.strip()) == 0) or (len(telefone.strip()) == 0):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/pacientes/')

        if not idade.isnumeric():
            messages.add_message(request, constants.ERROR, 'Digite uma idade válida')
            return redirect('/pacientes/')

        pacientes = Pacientes.objects.filter(email=email)

        if pacientes.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um paciente com esse E-mail')
            return redirect('/pacientes/')

        try:
            paciente = Pacientes(
                nome=nome,
                sexo=sexo,
                idade=idade,
                email=email,
                telefone=telefone,
                nutri=request.user,
                historico_medico=historico_medico,  # Novos campos
                habitos_alimentares=habitos_alimentares,
                nivel_atividade_fisica=nivel_atividade_fisica,
                metas=metas,
            )

            paciente.save()

            messages.add_message(request, constants.SUCCESS, 'Paciente cadastrado com sucesso')
            return redirect('/pacientes/')
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('/pacientes/')


def dados_paciente_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'dados_paciente_listar.html', {'pacientes': pacientes})


@login_required
def dados_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id, nutri=request.user)  # Garante que o paciente pertence ao nutricionista
    dados_paciente = DadosPaciente.objects.filter(paciente=paciente)
    laudos = Laudo.objects.filter(paciente=paciente)  # Puxar os laudos

    if request.method == "GET":
        return render(request, 'dados_paciente.html',
                      {'paciente': paciente, 'dados_paciente': dados_paciente, 'laudos': laudos})

    elif request.method == "POST":
        if request.POST.get('action') == 'upload_laudo':  # Identificar se é um upload de laudo
            nome = request.POST.get('nome')
            descricao = request.POST.get('descricao')
            arquivo = request.FILES.get('arquivo')  # Pegar arquivo

            laudo = Laudo(paciente=paciente, nome=nome, descricao=descricao, arquivo=arquivo)
            laudo.save()
            messages.add_message(request, constants.SUCCESS, 'Laudo adicionado com sucesso.')
            return redirect(f'/dados_paciente/{id}/')  # Redirecionar
        else:  # Se não for upload de laudo, processar dados do paciente
            peso = request.POST.get('peso')
            altura = request.POST.get('altura')
            gordura = request.POST.get('gordura')
            musculo = request.POST.get('musculo')

            hdl = request.POST.get('hdl')
            ldl = request.POST.get('ldl')
            colesterol_total = request.POST.get('ctotal')
            triglicerídios = request.POST.get('triglicerídios')

            if not all(
                    x.replace('.', '', 1).isdigit() for x in
                    [peso, altura, gordura, musculo, colesterol_total, triglicerídios]):
                messages.add_message(request, constants.ERROR, 'Digite números nos campos')
                return redirect(f'/dados_paciente/{id}/')

            dado_paciente = DadosPaciente(paciente=paciente,
                                             data=datetime.now(),
                                             peso=peso,
                                             altura=altura,
                                             percentual_gordura=gordura,
                                             percentual_musculo=musculo,
                                             colesterol_hdl=hdl,
                                             colesterol_ldl=ldl,
                                             colesterol_total=colesterol_total,
                                             trigliceridios=triglicerídios)

            dado_paciente.save()

            messages.add_message(request, constants.SUCCESS, 'Dados cadastrados com sucesso')

            return redirect(f'/dados_paciente/{id}/')  # Redireciona para a página de dados do paciente

@csrf_exempt
def grafico_peso(request, id):
    paciente = Pacientes.objects.get(id=id)
    dados = DadosPaciente.objects.filter(paciente=paciente).order_by("data")

    pesos = [dado.peso for dado in dados]
    labels = list(range(len(pesos)))
    data = {'peso': pesos,
            'labels': labels}
    return JsonResponse(data)


def plano_alimentar_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'plano_alimentar_listar.html', {'pacientes': pacientes})


def plano_alimentar(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/plano_alimentar_listar/')

    if request.method == "GET":
        r1 = Refeicao.objects.filter(paciente=paciente).order_by('horario')
        opcao = Opcao.objects.all()
        return render(request, 'plano_alimentar.html', {'paciente': paciente, 'refeicao': r1, 'opcao': opcao, })


def refeicao(request, id_paciente):
    paciente = get_object_or_404(Pacientes, id=id_paciente)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/dados_paciente/')

    if request.method == "POST":
        titulo = request.POST.get('titulo')
        horario = request.POST.get('horario')
        carboidratos = request.POST.get('carboidratos')
        proteinas = request.POST.get('proteinas')
        gorduras = request.POST.get('gorduras')

        r1 = Refeicao(paciente=paciente,
                      titulo=titulo,
                      horario=horario,
                      carboidratos=carboidratos,
                      proteinas=proteinas,
                      gorduras=gorduras)

        r1.save()

        messages.add_message(request, constants.SUCCESS, 'Refeição cadastrada')
        return redirect(f'/plano_alimentar/{id_paciente}')


def opcao(request, id_paciente):
    if request.method == "POST":
        id_refeicao = request.POST.get('refeicao')
        imagem = request.FILES.get('imagem')
        descricao = request.POST.get("descricao")

        o1 = Opcao(refeicao_id=id_refeicao,
                    imagem=imagem,
                    descricao=descricao)

        o1.save()

        messages.add_message(request, constants.SUCCESS, 'Opção cadastrada')
        return redirect(f'/plano_alimentar/{id_paciente}')