from flask import Flask, render_template, request, redirect, url_for
from module.autenticacao import *
from module.tarefas import *
import sqlite3
app = Flask(__name__)

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

    if not erros():
        conect = conexao()
        cursor = conect.cursor()
        cursor.execute('SELECT id FROM User Where nome = ?',(username,))
        user_exists = cursor.fetchone
        if user_exists:
            erros['username'] = "Já existe um usuário com o mesmo nome"
            conect.close()
        conect.execute('INSERT INTO User (nome,senha) VALUES (?,?)'(username,senha))
        conect.commit()
        conect.close()

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

    if not erros:
        conect = conexao()
        cursor = conect.cursor()
        user = cursor.execute('SELECT * FROM User WHERE nome = ? AND senha = ?',(username,senha))
        if user:
            autenticar(username)
            return redirect('tarefas')
    else:
        erros['geral'] = 'Nome de usuário ou senha incorreto(s)'
        return render_template('login.html', erros=erros)
    return render_template('login.html', erros=erros)

@validar_usuario
@app.route('/tarefas')
def tarefas():
    tarefas_inicial = carregar_tarefas()
    tarefas = []
    if request.args and request.args.get('titulo'):
        for tarefa in tarefas_inicial:
            if request.args['titulo'] in tarefa['titulo']:
                tarefas.append(tarefa)

    if tarefas:
        return render_template('tarefas.html', tarefas=tarefas)
    return render_template('tarefas.html', tarefas=tarefas_inicial)

@validar_usuario
@app.route('/cadastrar-tarefa', methods=['GET', 'POST'])
def cadastrar_tarefa():
    if request.method == 'GET':
        return render_template('formulario_tarefa.html', view='cadastrar_tarefa')

    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    prazo = request.form.get('prazo')

    tarefas = carregar_tarefas()
    id_nova_tarefa = len(tarefas) + 1
    erros = validar_dados_tarefa(titulo, prazo, id_nova_tarefa)

    if not erros.items():
        arquivo_dados = open(f'data/tarefas/{usuario_autenticado()}.txt', 'a')
        titulo = titulo.replace('\n', '\\n')
        descricao = descricao.replace('\n', '\\n')

        arquivo_dados.write(f'{titulo}\n')
        arquivo_dados.write(f'{descricao if descricao else "Sem descrição."}\n')
        arquivo_dados.write(f'{prazo if prazo else "Sem prazo."}\n')
        arquivo_dados.write(f'{id_nova_tarefa}\n')

        return redirect('tarefas')
    else:
        return render_template('formulario_tarefa.html', erros=erros, view='cadastrar_tarefa')

@validar_usuario
@app.route('/logout')
def logout():
    # Criar uma def para sair corretamente
    return redirect('login')

@validar_usuario
@app.route('/remover-tarefa/<id>')
def remover_tarefa(id: str):
    username_atual = usuario_autenticado()
    conect = conexao()
    cursor = conect.cursor()
    user = cursor.execute('SELECT id FROM User WHERE nome = ?'(username_atual,)).fetchone()
    conect.execute('DELETE FROM Tarefa WHERE id = ? And user_id = ?', (user,user['id']))
    conect.commit()
    conect.close()
    return redirect(url_for('tarefas'))

@validar_usuario
@app.route('/editar-tarefa/<id>', methods=['GET', 'POST'])
def editar_tarefa(id: str):
    username_atual = usuario_autenticado()
    conect = conexao()
    tarefas = carregar_tarefas()
    for tarefa in tarefas:
        if tarefa['id'] == id:
            dados_tarefa = tarefa

    if request.method == 'GET':
        return render_template('formulario_tarefa.html', tarefa=dados_tarefa)
    
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    prazo = request.form.get('prazo')

    erros = validar_dados_tarefa(titulo, prazo, id)
    if erros.items():
        return render_template('formulario_tarefa.html', erros=erros, tarefa=dados_tarefa)

    for tarefa in tarefas:
        if tarefa['id'] == id:
            tarefa['titulo'] = titulo
            tarefa['descricao'] = descricao
            tarefa['prazo'] = prazo

    with open(f'data/tarefas/{usuario_autenticado()}.txt', 'w') as arquivo_tarefas:
        arquivo_tarefas.write('')
    with open(f'data/tarefas/{usuario_autenticado()}.txt', 'a') as arquivo_tarefas:
        for tarefa in tarefas:
            titulo = tarefa['titulo'].replace('\n', '\\n')
            descricao = tarefa['descricao'].replace('\n', '\\n')
            prazo = tarefa['prazo']

            arquivo_tarefas.write(f'{titulo}\n')
            arquivo_tarefas.write(f'{descricao if descricao else "Sem descrição."}\n')
            arquivo_tarefas.write(f'{prazo if prazo else "Sem prazo."}\n')
            arquivo_tarefas.write(f'{tarefa["id"]}\n')

    return redirect(url_for('tarefas'))