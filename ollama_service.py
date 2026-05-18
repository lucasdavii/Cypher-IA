# Importa a biblioteca requests.
# Ela permite que o Python envie pedidos para outros sistemas.
# Aqui, vamos usar para mandar uma pergunta para o Ollama.
import requests


# Cria uma função chamada perguntar_ollama.
# Essa função recebe um texto chamado "prompt".
# O prompt é a mensagem completa que queremos enviar para a IA.
def perguntar_ollama(prompt):

    # Essa URL é o endereço local do Ollama no seu computador
    # "11434" é a porta padrão onde o Ollama fica, ai a partir desse local host ela opera.
    # "/api/generate" é a rota usada para gerar uma resposta.
    url = "http://localhost:11434/api/generate"

    # aqui é os dados que vao ser enviados para o ollama
    # Isso é como preencher um formulário antes de enviar.
    dados = { 
    "model": "qwen2.5:3b",
    "prompt": prompt,
    "stream": False,
    "options": {
        "num_predict": 120,
        "temperature": 0.3
    }
}


    resposta = requests.post(url, json=dados) # aqui usei o requests para fazer as requisições HTTP, basicamente o python vai interagir com o ollama, post foi usado pq significa enviar os dados, que nem usei no cypher

    # Aqui a resposta que veio do Ollama vira JSON.
    # O JSON é tipo um pacote organizado com várias informações dentro.
    # Fazendo isso, o Python consegue pegar só a parte que a gente quer.
    resposta_json = resposta.json()

    # Aqui eu pego apenas o texto que a IA gerou.
    # O Ollama guarda esse texto dentro da chave "response".
    texto_gerado = resposta_json["response"]

    # Aqui eu devolvo esse texto para o arquivo que chamou essa função.
    # No nosso caso, quem vai receber isso depois é o cypher_ai.py.
    return texto_gerado