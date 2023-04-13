import os


# Varrer o diretório do parâmetro "caminho" e inseri-lo na lista arquivos que será retornada como resposta.
def listar_arquivos_diretorios(caminho):
    arquivos = []
    for raiz, diretorios, arquivos_lista in os.walk(caminho):
        for arquivo in arquivos_lista:
            arquivos.append([arquivo, raiz])
    return arquivos


# Salvar arquivo txt com os diretórios encontrados, retirando-os da lista arquivos e inserindo linha por linha.
# Estrutura das linhas [Nome_arquivo, diretório]
def salvar_arquivo_txt(lista_arquivos, nome_arquivo_txt):
    with open(nome_arquivo_txt, 'w', encoding='utf-8') as f:
        for x in lista_arquivos:
            linha = f"{x[0], x[1]} \n"
            f.write(linha)


# Somente para teste separado do programa main
if __name__ == "__main__":
    caminho_diretorio = input("Digite o caminho do diretório a ser varrido: ")
    nome_arquivo_saida = input("Digite o nome do arquivo .txt de saída: ")

    arquivos = listar_arquivos_diretorios(caminho_diretorio)
    salvar_arquivo_txt(arquivos, nome_arquivo_saida)

    print(f"Arquivo {nome_arquivo_saida} criado com sucesso!")
