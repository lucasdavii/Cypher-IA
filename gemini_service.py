# O os serve para trabalhar com informações do sistema e caminhos de arquivos.
# Aqui vou usar ele para achar o arquivo .env dentro da pasta backend.
import os

# O load_dotenv serve para carregar as informações que estão no arquivo .env.
# É ele que permite o Python enxergar a GEMINI_API_KEY sem a key ficar escrita direto no código.
from dotenv import load_dotenv

# Aqui eu importo a biblioteca oficial do Gemini.
# O genai é quem permite o Python conversar com a API do Gemini.
from google import genai


# O __file__ guarda o caminho completo deste arquivo Python.
# O dirname vem de "directory name" e pega só a pasta onde este arquivo está.
pasta_atual = os.path.dirname(__file__)

# Aqui eu monto o caminho até o arquivo .env.
# Como o gemini_service.py está dentro do backend, ele vai procurar backend/.env.
caminho_env = os.path.join(pasta_atual, ".env")

# Aqui eu carrego o arquivo .env usando o caminho certo.
# Isso evita erro quando eu rodo o Python de outra pasta no terminal.
load_dotenv(caminho_env)

# Aqui eu pego a key do Gemini que está salva no .env.
# os.getenv procura uma variável pelo nome, nesse caso GEMINI_API_KEY.
gemini_key = os.getenv("GEMINI_API_KEY")

# Aqui eu crio o cliente do Gemini.
# O client é como se fosse a conexão entre meu Python e a API do Google.
client = genai.Client(api_key=gemini_key)


def perguntar_gemini(prompt):
    # Essa função recebe um prompt, envia para o Gemini e devolve a resposta em texto.
    # Ela tem o mesmo papel do perguntar_ollama(), só que usa uma API online.

    # Aqui eu mando o prompt para o modelo do Gemini.
    # model define qual IA vai responder, e contents é o texto que vai ser enviado para ela.
    resposta = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    # Aqui eu retorno só o texto gerado pela IA.
    # Quem vai receber esse texto depois é o cypher_ai.py.
    return resposta.text
