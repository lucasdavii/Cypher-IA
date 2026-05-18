from flask import Flask, request, jsonify # aqui eu importo o Flask para criar o servidor, request para receber os dados do JS e jsonify para responder em JSON
from flask_cors import CORS # aqui eu importo o CORS para permitir que o JavaScript converse com o Python sem bloqueio
from dotenv import load_dotenv # aqui eu importo o dotenv para carregar as chaves que ficam salvas no arquivo .env
import requests # aqui eu importo o requests para fazer requisições HTTP para Ollama, Groq e Gemini
import os # aqui eu importo o os para trabalhar com caminhos de arquivos e variáveis de ambiente


pasta_atual = os.path.dirname(__file__) # aqui eu pego a pasta onde esse arquivo Python está, para achar o .env mesmo rodando o terminal de outro lugar
caminho_env = os.path.join(pasta_atual, ".env") # aqui eu monto o caminho completo até o arquivo .env dentro da pasta do backend
load_dotenv(caminho_env) # aqui eu carrego as informações do .env para o Python conseguir usar as chaves e o modelo local

app = Flask(__name__) # aqui eu crio o servidor Flask, que vai receber as mensagens do front-end
CORS(app) # aqui eu libero o acesso do HTML/JS ao Flask, evitando erro de CORS no navegador


GROQ_API_KEY = os.getenv("GROQ_API_KEY") # aqui eu pego a chave da Groq que está salva no arquivo .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # aqui eu pego a chave do Gemini que está salva no arquivo .env
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b") # aqui eu pego o modelo do Ollama; se não tiver no .env, ele usa qwen2.5:3b como padrão


INSTRUCAO_CYPHER = """
Você é a Cypher AI, uma inteligência artificial modular independente.

Responda sempre em português do Brasil.
Responda com no máximo 5 linhas, a menos que o usuário peça para explicar mais.
Seja direto, claro e útil.
Não use listas, tópicos ou markdown, a menos que o usuário peça.
Não use caracteres especiais de formatação como #, *, -, markdown ou títulos exagerados.
Não mande código, a não ser que o usuário peça código.
Não fique repetindo sua apresentação.
Use o histórico da conversa para entender mensagens curtas como sim, não, continua, explica mais e pode.
Seja ética, segura e objetiva.
Quando o usuário usar termos técnicos, explique de forma simples se ele pedir.

Seu foco é ajudar com programação, explicações, resumos, organização de projetos, dúvidas gerais e produtividade.
""" # aqui fica a personalidade principal da Cypher, agora como uma IA independente e sem ligação com o Pathora


def preparar_historico(historico):
    # essa função limpa o histórico que vem do JavaScript antes de mandar para a IA
    # isso evita mensagens quebradas, roles erradas ou textos vazios dentro da conversa

    if not historico: # se o JS não mandar histórico nenhum
        return [] # retorna uma lista vazia para o código continuar funcionando normalmente

    historico_limpo = [] # aqui eu vou guardar apenas as mensagens que estão no formato certo

    for item in historico: # aqui eu passo por cada item que veio dentro do histórico
        role = item.get("role") # aqui eu pego quem enviou a mensagem, podendo ser user ou assistant
        content = item.get("content") # aqui eu pego o texto da mensagem

        if role in ["user", "assistant"] and content: # aqui eu verifico se a mensagem tem um papel válido e se tem conteúdo
            historico_limpo.append({
                "role": role,
                "content": content
            }) # aqui eu adiciono a mensagem limpa na lista final

    return historico_limpo[-20:] # aqui eu retorno só as últimas 20 mensagens para não pesar muito a requisição da IA


def comandos_especiais(mensagem):
    # essa função cria respostas fixas da própria Cypher
    # a vantagem é que certas perguntas simples não precisam gastar API nem depender da IA externa

    texto = mensagem.lower().strip() # aqui eu deixo tudo minúsculo e removo espaços inúteis para facilitar a comparação

    if "quem é você" in texto or "quem e voce" in texto or "quem é vc" in texto or "quem e vc" in texto:
        return "Eu sou a Cypher AI, uma assistente modular criada em Python com Flask para conversar, explicar assuntos, ajudar com programação e organizar ideias."

    if "quem te criou" in texto or "quem fez você" in texto or "quem fez voce" in texto or "criador" in texto or "desenvolvedor" in texto:
        return "Fui desenvolvida por Lucas Davi como um projeto de inteligência artificial modular usando Python, Flask e integração com diferentes provedores de IA."

    if "o que você faz" in texto or "o que voce faz" in texto or "ajuda" in texto or "como você pode ajudar" in texto or "como voce pode ajudar" in texto:
        return "Posso ajudar com programação, explicações, resumos, organização de projetos, ideias para GitHub, dúvidas técnicas e respostas rápidas do dia a dia."

    if "modos" in texto or "modo da ia" in texto or "provedores" in texto or "ollama" in texto and "gemini" in texto and "groq" in texto:
        return "Eu posso funcionar com Ollama local, Gemini API ou Groq API. O modo escolhido no site define qual provedor vai gerar a resposta."

    if "github" in texto and ("postar" in texto or "subir" in texto or "publicar" in texto or "organizar" in texto):
        return "Para postar no GitHub, organize o projeto com backend, frontend, README.md, requirements.txt, .gitignore e .env.example. Nunca envie o .env real com suas chaves."

    if "readme" in texto:
        return "Um bom README deve explicar o que o projeto faz, tecnologias usadas, funcionalidades, como executar, exemplos de uso e autoria do projeto."

    if "api" in texto and ("o que é" in texto or "oq é" in texto or "explica" in texto):
        return "API é uma ponte entre sistemas. No seu projeto, o JavaScript manda uma mensagem para o Flask, e o Flask conversa com a IA escolhida."

    if "flask" in texto and ("o que é" in texto or "oq é" in texto or "explica" in texto):
        return "Flask é uma biblioteca Python usada para criar servidores web. No seu projeto, ele recebe a mensagem do site e devolve a resposta da Cypher."

    if "env" in texto or ".env" in texto:
        return "O .env serve para guardar informações sensíveis, como chaves de API e nomes de modelos. Ele não deve ser enviado para o GitHub."

    if "status" in texto or "servidor" in texto and "online" in texto:
        return "O servidor da Cypher roda em Flask na porta 5000. Para testar, abra http://localhost:5000 no navegador."

    return None # se a mensagem não combinar com nenhum comando especial, a função retorna None e deixa a IA responder normalmente


def perguntar_ollama(historico):
    # essa função manda a conversa para o Ollama local
    # o Ollama precisa estar aberto no computador para essa parte funcionar

    mensagens = [
        {
            "role": "system",
            "content": INSTRUCAO_CYPHER
        }
    ] # aqui eu começo a conversa com a instrução principal da Cypher

    mensagens.extend(historico) # aqui eu adiciono o histórico real da conversa depois da instrução principal

    resposta = requests.post(
        "http://localhost:11434/api/chat", # aqui é o endereço padrão do Ollama rodando localmente
        json={
            "model": OLLAMA_MODEL, # aqui eu uso o modelo escolhido no .env ou o padrão qwen2.5:3b
            "messages": mensagens, # aqui eu mando a conversa inteira no formato de chat
            "stream": False, # aqui eu peço para o Ollama devolver a resposta completa de uma vez
            "options": {
                "temperature": 0.4, # aqui eu deixo a resposta mais controlada e menos aleatória
                "num_predict": 220 # aqui eu limito o tamanho da resposta para não virar textão
            }
        },
        timeout=120 # aqui eu defino um tempo limite para evitar o servidor travado para sempre
    )

    dados = resposta.json() # aqui eu transformo a resposta do Ollama em JSON

    if "message" not in dados: # se o Ollama responder diferente do esperado, evita quebrar o servidor
        print("ERRO OLLAMA:", dados)
        return "Ollama deu erro. Confira se ele está aberto e se o modelo está correto."

    return dados["message"]["content"] # aqui eu retorno apenas o texto gerado pela IA


def perguntar_groq(historico):
    # essa função manda a conversa para a Groq
    # a Groq usa API online, então precisa de internet e da chave correta no .env

    if not GROQ_API_KEY: # se a chave da Groq não existir no .env
        return "A chave da Groq não foi encontrada no arquivo .env."

    mensagens = [
        {
            "role": "system",
            "content": INSTRUCAO_CYPHER
        }
    ] # aqui eu começo a conversa com a instrução principal da Cypher

    mensagens.extend(historico) # aqui eu adiciono o histórico da conversa

    resposta = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}" # aqui eu envio a chave da Groq para autorizar o uso da API
        },
        json={
            "model": "llama-3.1-8b-instant", # aqui eu defino o modelo da Groq que vai responder
            "messages": mensagens,
            "temperature": 0.4, # aqui eu deixo a resposta direta e com pouca viagem
            "max_tokens": 220 # aqui eu limito o tamanho da resposta
        },
        timeout=120
    )

    dados = resposta.json() # aqui eu transformo a resposta da Groq em JSON

    if "choices" not in dados: # se a Groq responder com erro, evita quebrar o servidor
        print("ERRO GROQ:", dados)
        return "Groq deu erro. Confira a chave da Groq no arquivo .env."

    return dados["choices"][0]["message"]["content"] # aqui eu pego só o texto da resposta gerada


def converter_historico_gemini(historico):
    # essa função converte o histórico para o formato que o Gemini entende
    # isso é necessário porque o Gemini usa role user e model, diferente do formato padrão user e assistant

    historico_gemini = [] # aqui eu crio uma lista vazia para guardar o histórico convertido

    for item in historico: # aqui eu passo por cada mensagem do histórico
        role = item.get("role") # aqui eu pego o papel da mensagem
        content = item.get("content") # aqui eu pego o texto da mensagem

        if not content: # se a mensagem não tiver texto
            continue # aqui eu pulo essa mensagem e vou para a próxima

        if role == "user": # se a mensagem veio do usuário
            role_gemini = "user" # no Gemini continua sendo user
        else: # se a mensagem veio da IA
            role_gemini = "model" # no Gemini a resposta da IA usa o nome model

        historico_gemini.append({
            "role": role_gemini,
            "parts": [
                {
                    "text": content
                }
            ]
        }) # aqui eu adiciono a mensagem no formato correto do Gemini

    return historico_gemini # aqui eu retorno o histórico já convertido


def perguntar_gemini(historico):
    # essa função manda a conversa para o Gemini
    # o Gemini usa API online do Google, então precisa da chave correta no .env

    if not GEMINI_API_KEY: # se a chave do Gemini não existir no .env
        return "A chave do Gemini não foi encontrada no arquivo .env."

    historico_gemini = converter_historico_gemini(historico) # aqui eu converto o histórico para o formato aceito pelo Gemini

    resposta = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
        headers={
            "Content-Type": "application/json"
        },
        json={
            "contents": historico_gemini,
            "systemInstruction": {
                "parts": [
                    {
                        "text": INSTRUCAO_CYPHER
                    }
                ]
            },
            "generationConfig": {
                "temperature": 0.5, # aqui eu deixo a resposta equilibrada
                "maxOutputTokens": 500, # aqui eu dou limite para a resposta não ficar gigante
                "thinkingConfig": {
                    "thinkingBudget": 0 # aqui eu tento reduzir processamento extra para a resposta vir mais direta
                }
            }
        },
        timeout=120
    )

    dados = resposta.json() # aqui eu transformo a resposta do Gemini em JSON

    if "candidates" not in dados: # se o Gemini responder com erro, evita quebrar o servidor
        print("ERRO GEMINI:", dados)
        return "Gemini deu erro. Confira a chave do Gemini no arquivo .env."

    candidato = dados["candidates"][0] # aqui eu pego a primeira resposta gerada pelo Gemini

    if "content" not in candidato: # se a resposta vier sem conteúdo
        print("RESPOSTA GEMINI SEM CONTENT:", dados)
        return "Gemini não conseguiu gerar resposta completa."

    return candidato["content"]["parts"][0]["text"] # aqui eu retorno apenas o texto da resposta


@app.route("/", methods=["GET"])
def inicio():
    # essa rota serve apenas para testar se o servidor Flask está ligado
    # se abrir http://localhost:5000 e aparecer essa mensagem, o backend está funcionando

    return jsonify({
        "status": "Cypher AI está online."
    })


@app.route("/chat", methods=["POST"])
def chat():
    # essa é a rota principal do projeto
    # é ela que o JavaScript chama quando o usuário envia uma mensagem no chat

    dados = request.get_json() # aqui eu pego os dados que vieram do JavaScript em formato JSON

    if dados is None: # se o front-end não mandou nada
        return jsonify({"resultado": "Nenhum dado foi recebido pelo servidor."})

    mensagem = dados.get("mensagem", "") # aqui eu pego a mensagem digitada pelo usuário
    modo = dados.get("modo", "ollama") # aqui eu pego o modo escolhido no select: ollama, gemini ou groq
    historico = dados.get("historico", []) # aqui eu pego o histórico da conversa enviado pelo JavaScript

    if mensagem.strip() == "": # se a mensagem estiver vazia
        return jsonify({"resultado": "Digite uma mensagem antes de enviar."})

    historico = preparar_historico(historico) # aqui eu limpo o histórico antes de usar

    resposta_especial = comandos_especiais(mensagem) # aqui eu verifico se a mensagem pode ser respondida direto pelo próprio Python

    if resposta_especial:
        return jsonify({"resultado": resposta_especial}) # se for comando especial, responde sem chamar Ollama, Gemini ou Groq

    if len(historico) == 0 or historico[-1].get("content") != mensagem:
        historico.append({
            "role": "user",
            "content": mensagem
        }) # aqui eu garanto que a mensagem atual esteja dentro do histórico antes de mandar para a IA

    try:
        if modo == "ollama": # se o usuário escolheu Ollama
            resultado = perguntar_ollama(historico)

        elif modo == "gemini": # se o usuário escolheu Gemini
            resultado = perguntar_gemini(historico)

        elif modo == "groq": # se o usuário escolheu Groq
            resultado = perguntar_groq(historico)

        else: # se o modo vier errado do front-end
            resultado = "Modo de IA inválido. Escolha ollama, gemini ou groq."

    except Exception as erro:
        print("ERRO REAL:", erro) # aqui eu mostro o erro real no terminal para facilitar o debug
        resultado = "Erro real no Python: " + str(erro) # aqui eu devolvo o erro para aparecer na tela durante os testes

    return jsonify({"resultado": resultado}) # aqui eu devolvo a resposta final para o JavaScript mostrar no chat


if __name__ == "__main__":
    app.run(debug=True, port=5000) # aqui eu inicio o servidor Flask na porta 5000