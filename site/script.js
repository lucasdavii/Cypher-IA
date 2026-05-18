const btnEnviar = document.querySelector("#btn-enviar") // aqui eu pego o botão de enviar
const inputMensagem = document.querySelector("#mensagem") // aqui eu pego o input onde o usuário digita
const modoIa = document.querySelector("#modo-ia") // aqui eu pego o select onde o usuário escolhe Ollama, Gemini ou Groq
const chatCypher = document.querySelector(".chat-cypher") // aqui eu pego a área onde as mensagens vão aparecer

let historico = [] // aqui eu crio uma lista para guardar a conversa e mandar contexto para a IA

btnEnviar.addEventListener("click", enviarMensagem) // aqui eu faço o botão chamar a função quando for clicado

inputMensagem.addEventListener("keydown", (evento) => {
    // aqui eu faço o Enter também enviar a mensagem

    if (evento.key === "Enter") {
        enviarMensagem()
    }
})

async function enviarMensagem() {
    // essa função vai pegar a mensagem, mandar para o Python e mostrar a resposta na tela

    const mensagem = inputMensagem.value.trim() // aqui eu pego o texto digitado e removo espaços inúteis no começo e no fim

    if (mensagem === "") {
        alert("Digite uma mensagem antes de enviar.")
        return
    }

    adicionarMensagemNaTela(mensagem, "usuario") // aqui eu mostro a mensagem do usuário na tela

    historico.push({
        role: "user",
        content: mensagem
    }) // aqui eu salvo a mensagem do usuário no histórico

    inputMensagem.value = "" // aqui eu limpo o campo depois de enviar

    adicionarMensagemNaTela("Pensando...", "ia") // aqui eu mostro uma mensagem temporária enquanto a IA responde

    try {
        const resposta = await fetch("http://localhost:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                mensagem: mensagem,
                modo: modoIa.value,
                historico: historico
            })
        }) // aqui o JS envia a mensagem, o modo escolhido e o histórico para o Flask

        const dados = await resposta.json() // aqui eu transformo a resposta do Python em JSON

        removerMensagemPensando() // aqui eu removo o "Pensando..." da tela

        adicionarMensagemNaTela(dados.resultado, "ia") // aqui eu mostro a resposta da IA na tela

        historico.push({
            role: "assistant",
            content: dados.resultado
        }) // aqui eu salvo a resposta da IA no histórico

    } catch (erro) {
        removerMensagemPensando() // aqui eu removo o "Pensando..." se der erro

        adicionarMensagemNaTela("Erro ao conectar com o servidor Flask. Confira se o Python está rodando.", "ia") // aqui eu aviso o erro na tela

        console.log("Erro real:", erro) // aqui eu mostro o erro real no console do navegador
    }
}

function adicionarMensagemNaTela(texto, tipo) {
    // essa função cria uma mensagem nova dentro do chat

    const novaMensagem = document.createElement("div") // aqui eu crio uma div nova
    novaMensagem.classList.add("msg") // aqui eu adiciono a classe geral de mensagem
    novaMensagem.classList.add(tipo) // aqui eu adiciono usuario ou ia

    if (texto === "Pensando...") {
        novaMensagem.classList.add("pensando")
    } // aqui eu marco a mensagem temporária para conseguir apagar depois

    novaMensagem.textContent = texto // aqui eu coloco o texto dentro da div

    chatCypher.appendChild(novaMensagem) // aqui eu coloco a mensagem dentro do chat

    chatCypher.scrollTop = chatCypher.scrollHeight // aqui eu faço o chat descer automaticamente para a última mensagem
}

function removerMensagemPensando() {
    // essa função remove a mensagem temporária "Pensando..."

    const mensagemPensando = document.querySelector(".pensando") // aqui eu procuro a mensagem temporária

    if (mensagemPensando) {
        mensagemPensando.remove()
    } // se ela existir, eu removo da tela
}