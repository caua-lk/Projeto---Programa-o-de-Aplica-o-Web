from flask import Flask, render_template, request, redirect, url_for
from module.autenticacao import *
from module.tarefas import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, UserMixin, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sqla

app = Flask(__name__)
app.secret_key = 'ca26f724-c05e-4116-aad9-0a6383ce4386'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banck.db'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario,user_id)

db = SQLAlchemy(app)

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    nome = db.Column(db.String(80), unique=True,nullable=False)
    senha = db.Column(db.String(255),nullable=False)
    
class Tarefa(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.Text())
    prazo = db.Column(db.DateTime())
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

@app.route('/')
def index():
    if not current_user.is_authenticated:
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
        user_exists = db.session.execute(db.select(Usuario).filter_by(nome=username)).scalar()
        
        if user_exists:
            erros['username'] = "Já existe um usuário com o mesmo nome"
        else:
            hashed = generate_password_hash(senha)
            usuario = Usuario(nome=username,senha=hashed)
            
            db.session.add(usuario)
            db.session.commit()

            login_user(usuario)
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
        user = db.session.execute(db.select(Usuario).filter_by(nome=username)).scalars().first()

        if user and check_password_hash(user.senha,senha):
            login_user(user)
            return redirect(url_for('tarefas'))
        else:
            erros['geral'] = 'Nome de usuário ou senha incorreto(s)'
            return render_template('login.html', erros=erros)
    else:
        erros['geral'] = 'Nome de usuário ou senha incorreto(s)'
        return render_template('login.html', erros=erros)

@validar_usuario
@app.route('/tarefas')
@login_required
def tarefas():
    user_id = current_user.id
    
    tarefas = db.session.execute(db.select(Tarefa).filter_by(usuario_id=user_id)).scalars().all()
    
    return render_template('tarefas.html', tarefas=tarefas)

@validar_usuario
@app.route('/cadastrar-tarefa', methods=['GET', 'POST'])
@login_required
def cadastrar_tarefa():
    if request.method == 'GET':
        return render_template('formulario_tarefa.html', view='cadastrar_tarefa')

    from datetime import datetime

    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    prazo = request.form.get('prazo')
    erros = {}
    if not titulo:
        erros['titulo'] = 'Digite um título para cadastrar a tarefa.'
    if not prazo:
        erros['prazo'] = 'Defina um prazo para cadastrar a tarefa.'
    # tarefas = carregar_tarefas()
    # id_nova_tarefa = len(tarefas) + 1
    if erros:
        return render_template('formulario_tarefa.html', erros=erros, tarefa=None)

    tarefa = Tarefa(nome=titulo,descricao=descricao,prazo=datetime.strptime(prazo, '%Y-%m-%d'),usuario_id=current_user.id)
    db.session.add(tarefa)
    db.session.commit()

    return redirect(url_for('tarefas'))

@validar_usuario
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@validar_usuario
@app.route('/remover-tarefa/<id>')
@login_required
def remover_tarefa(id: str):
    user_id = current_user.id
    tarefa = db.session.execute(db.select(Tarefa).filter_by(usuario_id=user_id,id=id)).scalars().first()
    if tarefa:
        db.session.delete(tarefa)
        db.session.commit()
    return redirect(url_for('tarefas'))

@validar_usuario
@app.route('/editar-tarefa/<id>', methods=['GET', 'POST'])
@login_required
def editar_tarefa(id: str):
    user_id = current_user.id
    tarefa = db.session.execute(db.select(Tarefa).filter_by(usuario_id=user_id,id=id)).scalars().first()
    if not tarefa:
        return redirect(url_for('tarefas'))
    if request.method == 'GET':
        return render_template('formulario_tarefa.html', tarefa=tarefa, erros={})
    
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    prazo = request.form.get('prazo')
    erros = {}

    if not titulo:
        erros['titulo'] = 'Digite um título para cadastrar a tarefa.'
    if not prazo:
        erros['prazo'] = 'Defina um prazo para cadastrar a tarefa.'
    if erros:
        return render_template('formulario_tarefa.html', tarefa=tarefa, erros=erros)

    tarefa.nome = titulo
    tarefa.prazo = prazo
    if descricao:
        tarefa.descricao = descricao
    db.session.commit()
    return redirect(url_for('tarefas'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) # Desativar o debug para entregar