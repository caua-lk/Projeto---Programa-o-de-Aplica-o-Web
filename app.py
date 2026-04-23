from flask import Flask, render_template, request, redirect, url_for
from module.autenticacao import *
from module.tarefas import *

app = Flask(__name__)

usuario = None

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

@validar_usuario
@app.route('/tarefas')
def tarefas():
    return render_template('tarefas.html', tarefas=carregar_tarefas())

@validar_usuario
@app.route('/cadastrar-tarefa', methods=['GET', 'POST'])
def cadastrar_tarefa():
    if request.method == 'GET':
        return render_template('formulario_tarefa.html', view='cadastrar_tarefa')

    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    prazo = request.form.get('prazo')
    erros = validar_dados_tarefa(titulo, prazo)

    if not erros.items():
        arquivo_dados = open(f'data/tarefas/{usuario_autenticado()}.txt', 'a')
        arquivo_dados.write(f'{titulo}\n')
        arquivo_dados.write(f'{descricao}\n')
        arquivo_dados.write(f'{prazo}\n')

        with open(f'data/tarefas/{usuario_autenticado()}.txt') as arquivo_dados_r:
            linhas = arquivo_dados_r.readlines()

            if len(linhas) == 0:
                arquivo_dados.write('1\n')
            else:
                arquivo_dados.write(f'{int((len(linhas)) / 4 + 1)}\n')

        return redirect('tarefas')
    else:
        return render_template('formulario_tarefa.html', erros=erros, view='cadastrar_tarefa')

@validar_usuario
@app.route('/logout')
def logout():
    global usuario
    usuario = None

    arquivo = open('data/usuario.txt', 'w')
    arquivo.write('')
    return redirect('login')

@validar_usuario
@app.route('/remover-tarefa/<id>')
def remover_tarefa(id: str):
    tarefas = carregar_tarefas()
    for tarefa in tarefas:
        if tarefa['id'] == id:
            tarefas.remove(tarefa)

    with open(f'data/tarefas/{usuario_autenticado()}.txt', 'w') as arquivo_tarefas:
        arquivo_tarefas.write('')
    with open(f'data/tarefas/{usuario_autenticado()}.txt', 'a') as arquivo_tarefas:
        for tarefa in tarefas:
            arquivo_tarefas.write(f'{tarefa["titulo"]}\n')
            arquivo_tarefas.write(f'{tarefa["descricao"]}\n')
            arquivo_tarefas.write(f'{tarefa["prazo"]}\n')
            arquivo_tarefas.write(f'{tarefa["id"]}\n')

    return redirect(url_for('tarefas'))

@validar_usuario
@app.route('/editar-tarefa/<id>', methods=['GET', 'POST'])
def editar_tarefa(id: str):
    if request.method == 'GET':
        return render_template('formulario_tarefa.html', id=id)
    
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    prazo = request.form.get('prazo')

    erros = validar_dados_tarefa(titulo, prazo)
    if erros.items():
        return render_template('formulario_tarefa.html', erros=erros, id=id)

    tarefas = carregar_tarefas()
    for tarefa in tarefas:
        if tarefa['id'] == id:
            tarefa['titulo'] = titulo
            tarefa['descricao'] = descricao
            tarefa['prazo'] = prazo

    with open(f'data/tarefas/{usuario_autenticado()}.txt', 'w') as arquivo_tarefas:
        arquivo_tarefas.write('')
    with open(f'data/tarefas/{usuario_autenticado()}.txt', 'a') as arquivo_tarefas:
        for tarefa in tarefas:
            arquivo_tarefas.write(f'{tarefa["titulo"]}\n')
            arquivo_tarefas.write(f'{tarefa["descricao"]}\n')
            arquivo_tarefas.write(f'{tarefa["prazo"]}\n')
            arquivo_tarefas.write(f'{tarefa["id"]}\n')

    return redirect(url_for('tarefas'))