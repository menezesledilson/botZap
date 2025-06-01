from WPP_Whatsapp import Create
import time
import re
import os

# ✅ Função para carregar contatos proibidos (números formatados como no WhatsApp: ex: 553298389378)
#def carregar_contatos_proibidos(caminho="D:\\bots\\Atendimento-Whatsapp-Python\\contatos.txt"):

def carregar_contatos_proibidos(caminho=r"D:\bots\bot\contatos.txt"):
    contatos = set()
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if linha:
                    numero_normalizado = re.sub(r'\D', '', linha)  # Remove tudo que não for número
                    if numero_normalizado:
                        contatos.add(numero_normalizado)
    except FileNotFoundError:
        print(f"⚠️ Arquivo '{caminho}' não encontrado.")
    return contatos

# Carrega contatos proibidos ao iniciar o bot
#contatos_proibidos = carregar_contatos_proibidos()
# Função que sempre retorna a versão atualizada do arquivo

def get_contatos_proibidos():
    return carregar_contatos_proibidos()


# Criação da sessão do WhatsApp
your_session_name = "test"
creator = Create(session=your_session_name, headless=False)

client = creator.start()

print("🔄 Aguardando conexão com o WhatsApp...")
print("📡 Status da conexão:", creator.state)

if creator.state != 'CONNECTED':
    raise Exception("❌ Falha na conexão: " + creator.state)

print("✅ Conectado ao WhatsApp com sucesso!")

# Marca o momento de início do bot
start_time = int(time.time())

# Contexto por usuário
contextos_usuario = {}

# Menu principal
menu_msg = (
    "Olá! 👋 Seja muito bem-vindo ao nosso atendimento automático.\n\n"
    "Por favor, escolha uma das opções abaixo para que eu possa ajudar você:\n"
    "1️⃣ - Atendimento Pier (Life)\n"
    "2️⃣ - Atendimento Arthur (Benvita)\n"
    "3️⃣ - Suporte de Informática (Ledir)\n\n"
    "_Digite o número da opção que deseja._"
)

respostas_fixas = {
    "1": (
        "📋 Atendimento Pier (Life):\n"
        "Se você é produtor, por favor, envie os dados abaixo para que possamos continuar o atendimento:\n\n"
        "- Nome completo\n"
        "- CPF\n"
        "- Cidade onde você mora\n\n"
        "📌 Se seu assunto for outro, envie uma breve descrição para que possamos direcionar melhor o seu atendimento."
    ),
    "2": (
        "📋 Atendimento Arthur (Benvita):\n"
        "Se você é produtor, por favor, envie os dados abaixo para que possamos continuar o atendimento:\n\n"
        "- Nome completo\n"
        "- CPF\n"
        "- Cidade onde você mora\n\n"
        "📌 Se seu assunto for outro, envie uma breve descrição para que possamos direcionar melhor o seu atendimento."
    ),
    "3": (
        "💻 Setor de Informática:\n"
        "Se precisar de ajuda com sistemas ou algum problema técnico, por favor, explique sua situação para que possamos ajudar."
    ),
}

# Função chamada sempre que uma nova mensagem é recebida
def new_message(message):
    global client, contextos_usuario

    # Ignora mensagens antigas (enviadas antes do script iniciar)
    msg_timestamp = message.get("t")
    if msg_timestamp and msg_timestamp < start_time:
        print("⏳ Mensagem antiga ignorada.")
        return

    chat_id = message.get("from")
    numero = chat_id.split('@')[0]

    if numero in get_contatos_proibidos():
        print(f"🚫 Contato {numero} está na lista proibida. Mensagem ignorada.")
        return

    print("📩 Mensagem recebida:", message)

    if message and not message.get("isGroupMsg"):
        message_id = message.get("id")
        texto_usuario = message.get("body").strip().lower()
        agora = int(time.time())

        # Resetar o contexto
        if texto_usuario in ["0", "voltar"]:
            contextos_usuario.pop(chat_id, None)
            contextos_usuario[chat_id] = {"ultimo_menu": agora}
            client.reply(chat_id, "Você voltou ao menu principal.\n\n" + menu_msg, message_id)
            return

        # Encerrar conversa
        if texto_usuario in ["ok", "obrigado"]:
            contextos_usuario.pop(chat_id, None)
            client.reply(chat_id, "Encerrando atendimento. Até logo! 👋", message_id)
            return

        contexto = contextos_usuario.get(chat_id, {})

        # Usuário ainda não escolheu setor
        if "setor" not in contexto:
            ultimo_menu = contexto.get("ultimo_menu")
            tempo_passado = (agora - ultimo_menu) if ultimo_menu else None

            if texto_usuario in respostas_fixas:
                # Usuário escolheu um setor válido
                contextos_usuario[chat_id] = {
                    "setor": texto_usuario,
                    "em_conversa": False
                }
                client.reply(chat_id, respostas_fixas[texto_usuario] + "\n\nDigite sua dúvida ou escreva *0* para retornar ao menu.", message_id)
                return

            # Se nunca viu o menu ou já passaram 12 horas
            if not ultimo_menu or tempo_passado >= 43200:
                contextos_usuario[chat_id] = {
                    "ultimo_menu": agora
                }
                client.reply(chat_id, menu_msg, message_id)
            else:
                print(f"⏱ Menu não reenviado. Apenas {tempo_passado // 60} min desde o último envio.")
        else:
            # Já escolheu setor, responde conforme a lógica atual
            if not contexto.get("em_conversa"):
                setor = contexto.get("setor")
                if setor == "1":
                    resposta = "📌 Atendimento Pier (Life):\n Sua mensagem foi registrada. Um atendente responderá em breve."
                elif setor == "2":
                    resposta = "📌 Atendimento Arthur (Benvita): \n Sua mensagem foi registrada. Um atendente responderá em breve."
                elif setor == "3":
                    resposta = "📌 Informática: Sua solicitação foi registrada. Um técnico responderá em breve."
                else:
                    resposta = "📌 Sua mensagem foi registrada. Um atendente responderá em breve."

                contextos_usuario[chat_id]["em_conversa"] = True
                client.reply(chat_id, resposta + "\n\n(_Digite *0* para retornar ao menu ou *4* para encerrar._)", message_id)
            else:
                print(f"💬 [{chat_id}] Mensagem do usuário em conversa: {texto_usuario}")

# Iniciar escuta
creator.client.onMessage(new_message)

print("🤖 Bot do WhatsApp está rodando...")

# Mantém o script ativo
while True:
    time.sleep(1)
