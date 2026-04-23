from flask import Flask, render_template, request, redirect

app = Flask(__name__)

usuario = None

def autenticar(username: str) -> None:
    global usuario
    usuario = username

    arquivo = open('data/usuario.txt', 'w')
    arquivo.write(username)

def usuario_autenticado() -> str | None:
    arquivo = open('data/usuario.txt')
    if not arquivo.read():
        return None
    return arquivo.read()

@app.route('/')
def index():
    if not usuario:
        return render_template('index.html')
    redirect('tarefas')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'GET':
        return render_template('cadastro.html')

    username = request.form.get('username')
    senha = request.form.get('senha')
    confirmacao = request.form.get('confirmacao')
    erros = {}

    if not username:
        erros['username'] = 'Digite um nome de usuário para se cadastrar.'
    if not senha:
        erros['senha'] = 'Digite uma senha para se cadastrar.'
    if not confirmacao:
        erros['confirmacao'] = 'Confirme sua senha para se cadastrar.'
    if senha and confirmacao and senha != confirmacao:
        erros['confirmacao'] = 'Confirmação incorreta.'

    if not erros.items():
        arquivo_dados = open('data/usuarios.txt', 'w')
        arquivo_dados.write(f'{username}\n')
        arquivo_dados.write(f'{senha}\n')

        open(f'data/tarefas/{username}.txt', 'x')

        autenticar(username)
        return redirect('tarefas')
    else:
        return render_template('cadastro.html', erros=erros)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    senha = request.form.get('senha')
    erros = {}

    if not username:
        erros['username'] = 'Digite seu nome de usuário para logar.'
    if not senha:
        erros['senha'] = 'Digite uma senha para logar.'

    arquivo_dados = open('data/usuarios.txt')
    dados = arquivo_dados.readlines()
    
    for n in range(0, len(dados), 2):
        _username = dados[n][:len(dados[n]) - 1]
        _senha = dados[n + 1][:len(dados[n + 1]) - 1]
        if username == _username:
            if senha == _senha:
                autenticar(username)
                return redirect('tarefas')
    else:
        erros['geral'] = 'Nome de usuário ou senha incorreto(s)'
        return render_template('login.html', erros=erros)
    
@app.route('/tarefas')
def tarefas():
    if usuario_autenticado() is None:
        return redirect('login')

    arquivo_dados = open(f'data/tarefas/{usuario}.txt')
    dados = arquivo_dados.readlines()
    tarefas = []

    for n in range(0, len(dados), 3):
        tarefa = {
            'titulo': dados[n][:len(dados[n]) - 1],
            'descricao': dados[n + 1][:len(dados[n + 1]) - 1],
            'prazo': dados[n + 2][:len(dados[n + 2]) - 1]
        }
        tarefas.append(tarefa)

    return render_template('tarefas.html', tarefas=tarefas)

@app.route('/cadastrar-tarefa', methods=['GET', 'POST'])
def cadastrar_tarefa():
    if usuario_autenticado() is None:
        return redirect('login')

    if request.method == 'GET':
        return render_template('cadastrar_tarefa.html')

    from datetime import datetime

    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    prazo = request.form.get('prazo')
    erros = {}

    dt_atual = datetime.today()

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

    if not erros.items():
        arquivo_dados = open(f'data/tarefas/{usuario}.txt', 'a')
        arquivo_dados.write(f'{titulo}\n')
        arquivo_dados.write(f'{descricao}\n')
        arquivo_dados.write(f'{prazo}\n')

        return redirect('tarefas')
    else:
        return render_template('cadastrar_tarefa.html', erros=erros)

@app.route('/logout')
def logout():
    global usuario
    usuario = None

    arquivo = open('data/usuario.txt', 'w')
    arquivo.write('')
    return redirect('login')