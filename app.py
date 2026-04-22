from flask import Flask, render_template, request, redirect

app = Flask(__name__)

usuario = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'GET':
        return render_template('cadastro.html')

    global usuario

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

        usuario = username
        redirect('tarefas')
    else:
        return render_template('cadastro.html', erros=erros)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    global usuario

    username = request.form.get('username')
    senha = request.form.get('senha')
    erros = {}

    if not username:
        erros['username'] = 'Digite seu nome de usuário para logar.'
    if not senha:
        erros['senha'] = 'Digite uma senha para logar.'

    arquivo_dados = open('data/usuarios.txt')
    dados = arquivo_dados.readlines()
    
    for n in range(0, len(dados) - 2, 2):
        _username = dados[n][:len(dados[n]) - 2]
        _senha = dados[n + 1][:len(dados[n + 1]) - 2]
        if login == _username:
            if senha == _senha:
                usuario = _username
                redirect('tarefas')
    else:
        return render_template('login.html', usuario=usuario)
    
@app.route('/tarefas')
def tarefas():
    return render_template('tarefas.html')

@app.route('/cadastrar-tarefa', methods=['GET', 'POST'])
def cadastrar_tarefa():
    if request.method == 'GET':
        return render_template('cadastrar_tarefa.html')
    
    from datetime import datetime

    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    prazo = request.form.get('prazo')
    erros = {}

    if not titulo:
        erros['titulo'] = 'Digite um título para cadastrar a tarefa.'
    if prazo:
        ano_prazo = int(prazo[:4])
        if ano_prazo < datetime.year:
            erros['prazo'] = 'O prazo inserido já passou.'
        elif ano_prazo == datetime.year:
            mes_prazo = int(prazo[5:7])
            if mes_prazo < datetime.month:
                erros['prazo'] = 'O prazo inserido já passou.'
            elif mes_prazo == datetime.month:
                dia_prazo = int(prazo[8:])
                if dia_prazo < datetime.day:
                    erros['prazo'] = 'O prazo inserido já passou.'

    if not erros.items():
        arquivo_dados = open(f'data/tarefas/{usuario}.txt', 'a')
        arquivo_dados.write(f'{titulo}\n')
        arquivo_dados.write(f'{descricao}\n')
        arquivo_dados.write(f'{prazo}\n')
    else:
        return render_template('cadastrar_tarefa.html', erros=erros)

@app.route('/logout')
def logout():
    global usuario
    usuario = None
    redirect('login')