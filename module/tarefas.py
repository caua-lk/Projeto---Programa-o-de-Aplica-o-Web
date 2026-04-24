from .autenticacao import usuario_autenticado

def carregar_tarefas() -> list[dict[str, str]]:
    arquivo_dados = open(f'data/tarefas/{usuario_autenticado()}.txt')
    dados = arquivo_dados.readlines()
    tarefas = []

    for n in range(0, len(dados), 4):
        tarefa = {
            'titulo': dados[n][:len(dados[n]) - 1],
            'descricao': dados[n + 1][:len(dados[n + 1]) - 1],
            'prazo': dados[n + 2][:len(dados[n + 2]) - 1],
            'id': dados[n + 3][:len(dados[n + 3]) - 1]
        }
        tarefas.append(tarefa)

    return tarefas

def validar_dados_tarefa(titulo: str, prazo: str):
    from datetime import datetime

    erros = {}
    dt_atual = datetime.today()

    for tarefa in carregar_tarefas():
        if titulo == tarefa['titulo']:
            erros['titulo'] = 'Já existe uma tarefa com este título.'
            break

    if not titulo:
        erros['titulo'] = 'Digite um título para cadastrar a tarefa.'
    if prazo:
        ano_prazo = int(prazo[:4])
        if ano_prazo < dt_atual.year:
            erros['prazo'] = 'O prazo inserido já passou.'
        elif ano_prazo == dt_atual.year:
            mes_prazo = int(prazo[5:7])
            if mes_prazo < dt_atual.month:
                erros['prazo'] = 'O prazo inserido já passou.'
            elif mes_prazo == dt_atual.month:
                dia_prazo = int(prazo[8:])
                if dia_prazo < dt_atual.day:
                    erros['prazo'] = 'O prazo inserido já passou.'

    return erros