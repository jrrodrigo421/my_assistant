import os
from flask import Flask, render_template, request
from langchain_openai import OpenAI  # Certifique-se de que isso está configurado corretamente
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

api_key = os.getenv("API_KEY")
llm = OpenAI(api_key=api_key)  # Certifique-se de que o OpenAI está corretamente configurado

# Função para listar arquivos em um diretório
def listar_arquivos(diretorio):
    print(f"Listando arquivos no diretório: {diretorio}")
    arquivos = []
    for root, dirs, files in os.walk(diretorio):
        for file in files:
            if file.endswith((".py", ".dart", ".yaml")):  # Inclui arquivos Python, Dart e YAML
                arquivo_caminho = os.path.join(root, file)
                print(f"Arquivo encontrado: {arquivo_caminho}")
                arquivos.append(arquivo_caminho)
    return arquivos

# Função para ler o conteúdo de um arquivo com tratamento de codificação
def ler_arquivo(caminho_arquivo):
    print(f"Lendo arquivo: {caminho_arquivo}")
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            conteudo = file.read()
            print(f"Conteúdo do arquivo {caminho_arquivo}: {conteudo[:100]}...")  # Mostra os primeiros 100 caracteres
            return conteudo
    except UnicodeDecodeError:
        print(f"Erro de decodificação com UTF-8, tentando com Latin-1 para o arquivo {caminho_arquivo}")
        try:
            with open(caminho_arquivo, 'r', encoding='latin-1') as file:
                conteudo = file.read()
                print(f"Conteúdo do arquivo {caminho_arquivo}: {conteudo[:100]}...")  # Mostra os primeiros 100 caracteres
                return conteudo
        except Exception as e:
            erro_msg = f"Erro ao tentar ler o arquivo {caminho_arquivo}: {str(e)}"
            print(erro_msg)
            return erro_msg

# Função para chamar o modelo LLM e tratar erros de forma amigável
def chamar_llm(prompt):
    print(f"Chamando o modelo LLM com o prompt: {prompt[:100]}...")
    try:
        resposta = llm.invoke(prompt)
        print(f"Resposta do modelo: {resposta[:100]}...")
        return resposta
    except Exception as e:
        erro_msg = f"Erro ao chamar o modelo: {str(e)}"
        print(erro_msg)
        return erro_msg

@app.route("/", methods=["GET", "POST"])
def index():
    print("Rota / acessada")
    resposta = None
    analisado = False
    logs = []
    error_message = None

    if request.method == "POST":
        print("Método POST recebido")
        if 'path' in request.form:
            caminho_pasta = request.form['path']
            print(f"Caminho da pasta recebido: {caminho_pasta}")
            try:
                arquivos = listar_arquivos(caminho_pasta)
                for arquivo in arquivos:
                    logs.append(f"Analisando o arquivo: {arquivo}")
                    conteudo = ler_arquivo(arquivo)
                    if "Erro ao tentar ler o arquivo" in conteudo:
                        logs.append(conteudo)
                        continue
                    prompt = f"O seguinte código foi encontrado no arquivo {arquivo}. Explique o que ele faz e sugira melhorias:\n\n{conteudo}"
                    resposta = chamar_llm(prompt)  # Chamando o modelo diretamente
                    logs.append(f"Resposta do modelo para o arquivo {arquivo} processada: {resposta}")
                analisado = True
            except Exception as e:
                error_message = "Ocorreu um erro durante a análise. Por favor, verifique o caminho do diretório e tente novamente."
                logs.append(f"Erro: {str(e)}")
                print(f"Erro ao processar a pasta: {str(e)}")  # Log no console para depuração
        
        elif 'question' in request.form:
            pergunta = request.form['question']
            print(f"Pergunta recebida: {pergunta}")
            prompt = f"Sobre o projeto ou Flutter em geral, responda: {pergunta}"
            try:
                resposta = chamar_llm(prompt)  # Chamando o modelo diretamente
                logs.append(f"Pergunta: {pergunta}")
                logs.append(f"Resposta: {resposta}")
            except Exception as e:
                error_message = "Ocorreu um erro ao processar sua pergunta. Tente novamente mais tarde."
                logs.append(f"Erro: {str(e)}")
                print(f"Erro ao processar a pergunta: {str(e)}")  # Log no console para depuração

    print("Renderizando template com os seguintes dados:")
    print(f"analisado: {analisado}")
    print(f"resposta: {resposta}")
    print(f"logs: {logs}")
    print(f"error_message: {error_message}")
    
    return render_template("index.html", analisado=analisado, resposta=resposta, logs=logs, error_message=error_message)

if __name__ == "__main__":
    print("Iniciando aplicação Flask")
    app.run(debug=True)
