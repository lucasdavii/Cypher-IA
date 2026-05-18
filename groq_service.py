# O os serve para trabalhar com informações do sistema e caminhos de arquivos.
# Aqui vou usar ele para achar o arquivo .env dentro da pasta backend.
import os

# O load_dotenv carrega as informações salvas no arquivo .env.
# Assim a key da Groq fica fora do código e mais segura.
from dotenv import load_dotenv

# Aqui eu importo a biblioteca oficial da Groq.
# O Groq é o client usado para conversar com a API da Groq.
from groq import Groq


# O __file__ guarda o caminho completo deste arquivo Python.
# O dirname significa "directory name" e pega só a pasta onde o arquivo está.
pasta_atual = os.path.dirname(__file__)

# Aqui eu monto o caminho até o .env.
# Como esse arquivo está no backend, ele vai procurar o .env dentro do backend.
caminho_env = os.path.join(pasta_atual, ".env")

# Aqui eu carrego o .env usando o caminho exato.
# Isso evita o erro de o Python não encontrar a GROQ_API_KEY.
load_dotenv(caminho_env)

# Aqui eu pego a key da Groq que está dentro do .env.
# O nome precisa ser exatamente GROQ_API_KEY no arquivo .env.
groq_key = os.getenv("GROQ_API_KEY")

# Aqui eu crio o cliente da Groq.
# O client é a conexão entre meu código Python e a API da Groq.
client = Groq(api_key=groq_key)


def perguntar_groq(prompt):
    # Essa função recebe um prompt, manda para a Groq e devolve a resposta em texto.
    # Ela funciona igual à perguntar_ollama(), mas usando uma API online e rápida.

    # Aqui eu envio o prompt para o modelo da Groq.
    # messages é uma lista de mensagens no formato de chat, com role e content.
    resposta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        # temperature controla o quanto a IA pode variar/criar.
        # 0.3 deixa a resposta mais direta e menos viajada.
        temperature=0.3,

        # max_tokens limita o tamanho da resposta.
        # Isso ajuda a IA responder mais rápido e não fazer textão.
        max_tokens=180
    )

    # A Groq devolve a resposta dentro de choices[0].message.content.
    # Aqui eu pego só o texto final gerado pela IA.
    return resposta.choices[0].message.content
