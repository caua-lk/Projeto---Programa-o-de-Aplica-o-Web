from flask import Flask, render_template, request, redirect, url_for
from module.autenticacao import *
from module.tarefas import *
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sqla

app = Flask(__name__)
app.secret_key = 'ca26f724-c05e-4116-aad9-0a6383ce4386'

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(type_=db.Integer())
    nome = db.Column(type_=db.String(max_length=80))
    senha = db.Column(type_=db.String())


class Tarefa(db.Model):
    id = db.Column(type_=db.Integer())
    nome = db.Column(type_=db.String(max_length=80))
    descricao = db.Column(type_=db.Text())
    prazo = db.Column(type_=db.DateTime())
    usuario_id = db.Column(type_=db.ForeignKey(to=Usuario))

@app.route('/')
def index():
    if not session.get('user'):
        return render_template('index.html')

    return redirect(url_for('tarefas'))

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


    if not erros:
        conect = conexao()
        cursor = conect.cursor()
        cursor.execute('SELECT id FROM User Where nome = ?',(username,))
        user_exists = cursor.fetchone()
        if user_exists:
            erros['username'] = "Já existe um usuário com o mesmo nome"
            conect.close()
        cursor.execute('INSERT INTO User (nome,senha) VALUES (?,?)', (username,senha))
        conect.commit()

        user = cursor.execute('SELECT * FROM User WHERE nome = ?',(username,)).fetchone()
        session['user'] = user['nome']
        session['id'] = user['id']

        conect.close()
        return redirect(url_for('tarefas'))
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
        user = cursor.execute('SELECT * FROM User WHERE nome = ? AND senha = ?',(username,senha)).fetchone()
        if user:
            session['user'] = username
            session['id'] = user['id']
            return redirect('tarefas')
    else:
        erros['geral'] = 'Nome de usuário ou senha incorreto(s)'
        return render_template('login.html', erros=erros)
    return render_template('login.html', erros=erros)

@validar_usuario
@app.route('/tarefas')
def tarefas():
    tarefas_inicial = carregar_tarefas()
    if request.args and request.args.get('titulo'):
        tarefas = []
        for tarefa in tarefas_inicial:
            if request.args['titulo'] in tarefa['titulo']:
                tarefas.append(tarefa)
    else:
        tarefas = tarefas_inicial

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

    if erros:
        return render_template(
            'formulario_tarefa.html',
            erros=erros,
            tarefa=None
        )

    connect = conexao()
    cursor = connect.cursor()

    cursor.execute("""
        INSERT INTO Tarefa (nome, descricao, prazo, user_id) VALUES
        (?, ?, ?, ?)
    """, (titulo, descricao, prazo, session['id']))

    connect.commit()
    connect.close()

    return redirect(url_for('tarefas'))

@validar_usuario
@app.route('/logout')
def logout():
    session.pop('id')
    session.pop('user')
    return redirect('login')

@validar_usuario
@app.route('/remover-tarefa/<id>')
def remover_tarefa(id: str):
    conect = conexao()
    conect.execute(
        'DELETE FROM Tarefa WHERE id = ? AND user_id = ?',
        (id, session['id'])
    )
    conect.commit()
    conect.close()
    return redirect(url_for('tarefas'))

@validar_usuario
@app.route('/editar-tarefa/<id>', methods=['GET', 'POST'])
def editar_tarefa(id: str):
    conect = conexao()
    cursor = conect.cursor()
    tarefa = cursor.execute(
        '''
        SELECT id,
               nome AS titulo,
               descricao,
               prazo
        FROM Tarefa
        WHERE id = ? AND user_id = ?
        ''',
        (id, session['id'])
    ).fetchone()
    if request.method == 'GET':
        return render_template(
            'formulario_tarefa.html',
            tarefa=tarefa,
            erros={}
        )
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    prazo = request.form.get('prazo')
    erros = validar_dados_tarefa(titulo, prazo, int(id))
    if erros:
        return render_template(
            'formulario_tarefa.html',
            tarefa=tarefa,
            erros=erros
        )
    cursor.execute(
        '''
        UPDATE Tarefa
        SET nome = ?, descricao = ?, prazo = ?
        WHERE id = ? AND user_id = ?
        ''',
        (titulo, descricao, prazo, id, session['id'])
    )
    conect.commit()
    conect.close()
    return redirect(url_for('tarefas'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) # Desativar o debug para entregar