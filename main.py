# Importar bibliotecas necessárias
from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import psycopg2

# Instanciar o aplicativo Flask
app = Flask(__name__)

# Configurar o banco de dados
# banco_teste = nome do banco a ser conectado
db = 'postgresql'  # banco, pymysql = drive utilizado
db_drive = 'psycopg2'  # drive para acesso ao banco
db_username = 'postgres'  # usuário do banco de dados
db_password = 'admin000'  # senha
db_hostname = 'localhost'  # endereço do servidor do banco de dados
db_name = 'Rotas'  # nome do banco a ser utilizado

# Concatena as configurações na string de configuração do banco de dados do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'{db}+{db_drive}://{db_username}:{db_password}@{db_hostname}/{db_name}'

# Instancia o objeto para realizar as interações com o banco de dados
db = SQLAlchemy(app)


# Definir função para testar conexão com o banco de dados
def teste_conexao_banco():
    conexao = None
    try:
        conexao = db.engine.connect()
        conexao.execute(text('SELECT 1'))
        print("Conexão Realizada")
    except Exception as e:
        print(f"Erro ao conectar: {str(e)}")
    finally:
        if conexao:
            conexao.close()
            print("Conexão encerrada")


# Definir modelo da classe Arquivos conforme a tabela arquivos do banco de dados
class Arquivos(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(12), nullable=False)
    caminho = db.Column(db.String(200), nullable=False)
    modificacao = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    def __repr__(self):
        return f'{self.nome}: Caminho=[{self.caminho}] '


# ------------------- ROTAS E FUNÇÕES DO FLASK ----------------------
# Definir rota principal para a página inicial
@app.route("/")
def home():
    teste_conexao_banco()
    return render_template("index.html")


# Definir rota para listar valores da tabela arquivos
@app.route('/arquivos')
def listar_arquivos():
    arquivos = Arquivos.query.all()
    print(arquivos)

    if not arquivos:
        return "Nenhum arquivo encontrado."
    elif len(arquivos) == 1:
        return str(arquivos[0])
    else:
        return ', '.join(str(arquivo) for arquivo in arquivos)


# Definir rota para exibir o formulário de inserção de novos registros
@app.route('/formulario')
def formulario():
    return render_template('formulario.html')


# Definir rota para enviar dados do formulário
@app.route('/enviar', methods=['POST'])
def enviar():
    nome = request.form['nome']
    caminho = request.form['caminho']

    novo_arquivo = Arquivos(nome=nome, caminho=caminho)
    db.session.add(novo_arquivo)
    db.session.commit()

    return redirect(url_for('formulario'))


# Cria tabela caso não exista ainda
@app.route("/criar")
def criar_tabela():
    db.create_all()
    return "Tabela Criada com Sucesso"


# Executar o aplicativo Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
