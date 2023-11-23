from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
import re
from flask import jsonify
from flask_migrate import Migrate



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:senha123@127.0.0.1/petsoft'
app.config['SECRET_KEY'] = 'chave_secreta'  
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Definindo modelos para as tabelas do banco de dados
class Cliente(db.Model):
    idCliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(80), nullable=False)
    logradouro = db.Column(db.String(80), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

class Animal(db.Model):
    id_an = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(80), nullable=False)
    data_nasc = db.Column(db.Date)
    pelagem = db.Column(db.String(5))
    porte = db.Column(db.String(3))
    agressivo = db.Column(db.Boolean)
    obs = db.Column(db.String(100))

    # Chave estrangeira referenciando a tabela Cliente
    Cliente_idCliente = db.Column(db.Integer, db.ForeignKey('cliente.idCliente'), nullable=False)

    # Relacionamento com o Cliente
    cliente = db.relationship('Cliente', backref=db.backref('animais', lazy=True))


class Usuario(db.Model):
    id_us = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False)

class Servico(db.Model):
    id_ser = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo = db.Column(db.String(10))
    valor = db.Column(db.Float)

class OrdemDeServico(db.Model):
    id_os = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo = db.Column(db.String(10), nullable=False)
    descricao = db.Column(db.String(45), nullable=False)
    valorTotal = db.Column(db.Float, nullable=False)
    data_in = db.Column(db.Date)
    Usuario_id_us = db.Column(db.Integer, db.ForeignKey('usuario.id_us'), nullable=False)
    Cliente_idCliente = db.Column(db.Integer, db.ForeignKey('cliente.idCliente'), nullable=False)
    Animal_id_an = db.Column(db.Integer, db.ForeignKey('animal.id_an'), nullable=False)
    Animal_Cliente_idCliente = db.Column(db.Integer, nullable=False)


# Rotas
@app.route('/')
def redirecionar_para_login():
    return redirect(url_for('login'))

@app.route('/index')
def home():
    return render_template('index.html')

@app.route('/clientes', methods=['GET', 'POST'])
def listar_clientes():
    if request.method == 'GET':
        clientes = Cliente.query.all()
        return render_template('clientes.html', clientes=clientes)
    elif request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        telefone_cliente = request.form['telefone_cliente']
        endereco_cliente = request.form['endereco_cliente']

        # Server-side validation
        if not re.match(r"[A-Za-zÀ-ú ]+", nome_cliente):
            flash('O nome do cliente deve conter apenas letras e espaços.', 'error')
            return redirect(url_for('listar_clientes'))

        if not re.match(r"[0-9]{10,}", telefone_cliente):
            flash('Informe um número de telefone válido.', 'error')
            return redirect(url_for('listar_clientes'))

        # If validation passes, add the new client to the database
        novo_cliente = Cliente(nome=nome_cliente, telefone=telefone_cliente, logradouro=endereco_cliente)
        db.session.add(novo_cliente)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Um cliente com o mesmo nome já existe.', 'error')
        
        return redirect(url_for('listar_clientes'))


# Alteração na rota /animais para passar a lista de clientes para o template
@app.route('/animais', methods=['GET', 'POST'])
def listar_animais():
    if request.method == 'POST':
        # Obter os dados do formulário
        nome_animal = request.form.get('nome_animal')
        cliente_id = request.form.get('cliente_animal')

        # Verificar se o nome do animal não contém números
        if any(char.isdigit() for char in nome_animal):
            flash('O nome do animal não pode conter números.', 'error')
            return redirect(url_for('listar_animais'))

        # Verificar se o cliente existe
        cliente = Cliente.query.get(cliente_id)
        if cliente is None:
            flash('Cliente não encontrado.', 'error')
            return redirect(url_for('listar_animais'))

        # Verificar se o animal já tem um dono
        if Animal.query.filter_by(nome=nome_animal).first():
            flash('Já existe um animal com esse nome.', 'error')
            return redirect(url_for('listar_animais'))

        # Se todas as verificações passarem, criar o novo animal
        novo_animal = Animal(
            nome=nome_animal,
            data_nasc=datetime.now(),
            Cliente_idCliente=cliente_id
            # Adicione os outros campos do formulário conforme necessário
        )

        db.session.add(novo_animal)
        db.session.commit()

        flash('Animal adicionado com sucesso.', 'success')
        return redirect(url_for('listar_animais'))

    # Se for uma solicitação GET, continue com a lógica de listagem de animais
    animais = Animal.query.all()
    clientes = Cliente.query.all()
    return render_template('animais.html', animais=animais, clientes=clientes)


@app.route('/agendamento')
def listar_agendamento():
    agendamento = OrdemDeServico.query.all()
    return render_template('agendamento.html', agendamento=agendamento)

@app.route('/servicos')
def listar_servicos():
    servicos = Servico.query.all()
    return render_template('servicos.html', servicos=servicos)

@app.route('/servicos', methods=['POST'])
def adicionar_servico():
    tipo_servico = request.form['tipo_servico']
    valor_servico = float(request.form['valor_servico'])

    # Check if a service with the same type already exists
    existing_servico = Servico.query.filter_by(tipo=tipo_servico).first()
    if existing_servico:
        flash('Um serviço com este tipo já existe.', 'error')
        return redirect(url_for('listar_servicos'))

    novo_servico = Servico(tipo=tipo_servico, valor=valor_servico)
    db.session.add(novo_servico)
    db.session.commit()
    flash('Serviço adicionado com sucesso.', 'success')

    return redirect(url_for('listar_servicos'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Inicializa a mensagem de erro como None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifique as credenciais (substitua isso com sua lógica de autenticação real)
        if username == 'admin' and password == 'admin123':
            # Autenticação bem-sucedida, salve o usuário na sessão
            session['username'] = username

            # Redirecione para a página principal ou para a página que estava tentando acessar
            next_page = request.args.get('next', 'home')
            return redirect(url_for(next_page))

        else:
            # Credenciais inválidas, define a mensagem de erro
            error = 'Credenciais inválidas. Tente novamente.'

    # Se o método for GET ou as credenciais estiverem incorretas, exiba o formulário de login com a mensagem de erro
    return render_template('login.html', error=error)

# Proteção de rotas
@app.before_request
def before_request():
    # Lista de rotas públicas
    rotas_publicas = ['login', 'redirecionar_para_login']

    # Verifica se a rota está nas rotas públicas
    if request.endpoint and request.endpoint not in rotas_publicas:
        if 'username' not in session:
            return redirect(url_for('login', next=request.endpoint))


if __name__ == '__main__':
    #with app.app_context():
       # db.create_all()
    app.run(debug=True)


#     # Apaga o banco e recomeça
# with app.app_context():
#     db.drop_all()
#     db.create_all()