# Importar bibliotecas necessárias
from flask import Flask, redirect, url_for, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, desc
import psycopg2
import listagem_diretorios
import time

# Instanciar o aplicativo Flask
app = Flask(__name__)

# Configurar o banco de dados
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


# Tabela ArquivoDiretorio ("arquivo_diretorio" no postgresql)
class ArquivoDiretorio(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    arquivo = db.Column(db.String[10], nullable=False)
    diretorio = db.Column(db.String[250], nullable=False)
    timestamp = db.Column(db.DateTime, server_default=text('NOW()'))

    def __repr__(self):
        return f'{self.arquivo}, {self.diretorio}, {self.timestamp}'


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


# Função para ler o arquivo txt gerado após varrer o diretório solicitado e inserir as informações no banco de dados
def inserir_txt_no_banco(arquivo_txt):
    contagem_insercoes = 1
    with open(arquivo_txt, "r", encoding='utf-8') as txt:  # Selecionado encoding utf-8 para evitar erro de encoding
        for linha in txt:
            try:
                # manipula linha para inseri-la no banco sem caracteres especiais
                arquivo, diretorio = linha.replace("'", '').strip("('").replace(")", '').split(', ')
            except Exception:
                # ignora erro na formatação do nome do arquivo ou do diretório
                print(f'Problema na linha {contagem_insercoes} - Continuando a insercao e ignorando essa linha')
            else:
                # caso não haja erro na linha atual, ela é adicionada à pilha de registros a serem inseridos
                novo_arquivo = ArquivoDiretorio(arquivo=arquivo, diretorio=diretorio)
                db.session.add(novo_arquivo)
            contagem_insercoes += 1  # Contagem da quantidade de linhas inseridas
        db.session.commit()  # Insere toda a pilha acumulado ao banco de dados
    return contagem_insercoes


def limpar_tabela():
    ArquivoDiretorio.query.delete()
    # Reinicia contagem da coluna id após limpar a tabela
    query = text(f"ALTER SEQUENCE arquivo_diretorio_id_seq RESTART WITH 1")
    db.session.execute(query)
    db.session.commit()


# ------------------- ROTAS E FUNÇÕES DO FLASK ----------------------



# Cria tabelaS caso não existam ainda
@app.route("/criar")
def criar_tabela():
    db.create_all()
    return "Tabela Criada com Sucesso"


# --------------------------- LINKS MENU LATERAL --------------------------------

# Rota principal
@app.route("/")
def home():
    teste_conexao_banco()
    return render_template("index.html")

# Definir rota para inserir registros manualmente
@app.route('/insercao_manual')
def insercao_manual():
    return render_template('insercao_manual.html')

# Definir rota para alterar registros
@app.route('/alteracao_manual')
def alteracao_manual():
    return render_template('alteracao_manual.html')

# Definir rota para listar valores da tabela arquivos
@app.route('/tabela_leitura_registros')
def tabela_leitura_registros():
    arquivos = ArquivoDiretorio.query.order_by(desc(ArquivoDiretorio.timestamp)).all()
    limite_registros = min(len(arquivos), 10)
    return render_template('/tabela_leitura_registros.html', leitura=arquivos, limite=limite_registros)

# Página para definir o campo de diretório que será varrido
@app.route("/atualizar_arquivos")
def atualizar_registros():
    return render_template("/atualizar_registros.html")

# Página de ajuda
@app.route("/ajuda")
def ajuda():
    return render_template("/ajuda.html")


# --------------------------- FUNÇÕES --------------------------------
# Página chamada pelo html da página /atualizar_registros que retorna o diretório pelo parâmetro do request.form
# ['diretorio']
# Essa página que chama as funções para listar os arquivos numa lista que será passada para a função'salvar_arquivo_txt'
# que irá gerar um arquivo.txt com todos os registros e que será passado para a 'inserir_dados_arquivos_txt'
# e então serão inseridos no banco de dados
@app.route("/atualizar", methods=['POST'])
def atualizar():
    diretorio = request.form['diretorio']
    limpar_tabela()  # Limpa a tabela antes de atualizar os registros
    t_inicial = time.time()  # Salva tempo atual antes de executar as funções
    arquivos = listagem_diretorios.listar_arquivos_diretorios(diretorio)
    listagem_diretorios.salvar_arquivo_txt(arquivos, "ListaDiretorios.txt")

    # contagem_inseridos salva o valor de retorno da função inserir_dados_arquivo_txt que retorna a quantidade de
    # registros inseridos
    contagem_inseridos = inserir_txt_no_banco("ListaDiretorios.txt")
    t_final = time.time()  # Salva tempo atual após executar as funções
    t_total = t_final - t_inicial  # Calcula tempo total para varredura e inserção no banco
    return f"Atualização realizada - {contagem_inseridos} registros inserios - Levou {t_total} segundos"


# Definir rota para enviar dados do formulário
@app.route('/enviar', methods=['POST'])
def enviar():
    nome = request.form['form_manual_name']
    caminho = request.form['form_manual_path']
    novo_arquivo = ArquivoDiretorio(arquivo=nome, diretorio=caminho)
    db.session.add(novo_arquivo)
    db.session.commit()

    return redirect(url_for('insercao_manual'))


# Limpa toda a tabela arquivo_diretorio
@app.route("/limpar_tabela")
def comando_limpar_tabela():
    limpar_tabela()
    return redirect("/")

# Rota para pesquisar registro por nome de arquivo
@app.route("/buscar_registro", methods=['POST'])
def buscar_registro():
    nome_arquivo = request.form['nome_arquivo']
    registro = ArquivoDiretorio.query.filter_by(arquivo=nome_arquivo).first()
    if registro:
        return render_template('alteracao_manual.html', registro=registro)
    else:
        msg = "Registro não encontrado"
        return render_template('alteracao_manual.html', msg=msg)
    
# Rota para atualizar registro
@app.route("/alterar_registro", methods=['POST'])
def alterar_registro():
    registro_id = request.form['id']
    novo_arquivo = request.form['arquivo']
    novo_diretorio = request.form['diretorio']
    registro = ArquivoDiretorio.query.get(registro_id)
    if registro:
        registro.arquivo = novo_arquivo
        registro.diretorio = novo_diretorio
        db.session.commit()
        return redirect(url_for('tabela_leitura_registros'))
    else:
        return "Registro não encontrado"


# Executar o aplicativo Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
