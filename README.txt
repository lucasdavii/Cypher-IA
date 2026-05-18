# Cypher AI

Cypher AI é uma inteligência artificial modular desenvolvida em Python, com backend em Flask e integração com diferentes provedores de IA.

O projeto permite conversar com a IA pelo navegador e escolher entre modos como Ollama Local, Gemini API e Groq API.

## Tecnologias usadas

- Python
- Flask
- Flask-CORS
- JavaScript
- HTML
- CSS
- Ollama
- Gemini API
- Groq API
- Python Dotenv

## Funcionalidades

- Chat com inteligência artificial
- Escolha entre diferentes provedores de IA
- Integração com Ollama local
- Integração com Gemini API
- Integração com Groq API
- Uso de arquivo .env para proteger chaves de API
- Front-end próprio com HTML, CSS e JavaScript
- Backend em Flask
- Sistema de comandos especiais para respostas rápidas

## Estrutura do projeto

```txt
CYPHER-AI/
│
├── site/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── cypher_ai.py
├── gemini_service.py
├── groq_service.py
├── ollama_service.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md