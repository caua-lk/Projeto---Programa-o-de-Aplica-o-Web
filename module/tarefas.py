from .autenticacao import usuario_autenticado
from .bd import *
def carregar_tarefas() -> list[dict[str, str]]:
    conect = conexao()
    cursor = conect.cursor()
    tarefas = cursor('SELECT id,nome,descricao,prazo FROM Tarefa WHERE user_id = ?',(session['id'],)).fetchall()
    return tarefas

def validar_dados_tarefa(titulo: str, prazo: str, id: int):
    from datetime import datetime

    erros = {}
    dt_atual = datetime.today()

    for tarefa in carregar_tarefas():
        if titulo == tarefa['titulo'] and id != tarefa['id']:
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