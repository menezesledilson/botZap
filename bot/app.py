from WPP_Whatsapp import Create
from db import numero_bloqueado
import time
import re

# Função para verificar se o contato está bloqueado
def verificar_contato(numero):
    if numero_bloqueado(numero):
        print(f"🚫 Contato {numero} está na lista proibida. Ignorado.")
        return True
    return False

# Carrega contatos proibidos de arquivo (não usado atualmente)
def carregar_contatos_proibidos(caminho="banco/contatos.db"):    
    contatos = set()
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if linha:
                    numero_normalizado = re.sub(r'\D', '', linha)
                    if numero_normalizado:
                        contatos.add(numero_normalizado)
    except FileNotFoundError:
        print(f"⚠️ Arquivo '{caminho}' não encontrado.")
    return contatos

# Criação da sessão do WhatsApp
your_session_name = "test"
creator = Create(session=your_session_name, headless=False)
client = creator.start()

print("🔄 Aguardando conexão com o WhatsApp...")
print("📡 Status da conexão:", creator.state)

if creator.state != 'CONNECTED':
    raise Exception("❌ Falha na conexão: " + creator.state)

print("✅ Conectado ao WhatsApp com sucesso!")

start_time = int(time.time())
contextos_usuario = {}

menu_msg = (
    "Olá! 👋 Seja muito bem-vindo ao nosso atendimento automático.\n\n"
    "Por favor, escolha uma das opções abaixo para que eu possa ajudar você:\n"
    "1️⃣ - Atendimento Pier (Life)\n"
    "2️⃣ - Atendimento Arthur (Benvita)\n"
    "3️⃣ - Suporte de Técnico\n\n"
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
        "🛠 Suporte Técnico (T.I.)\n"
        "Para atendimento direto com nosso suporte de tecnologia, entre em contato pelo número abaixo:\n"
        "📞 (32) 9844-3282\n"
        "Ou clique aqui: wa.me/553298443282"
    ),
}

def new_message(message):
    global client, contextos_usuario

    msg_timestamp = message.get("t")
    if msg_timestamp and msg_timestamp < start_time:
        print("⏳ Mensagem antiga ignorada.")
        return

    chat_id = message.get("from")
    numero = chat_id.split('@')[0]
    numero = re.sub(r'\D', '', numero)  # Remove qualquer caractere que não seja número


    if verificar_contato(numero):
        return

    print("📩 Mensagem recebida:", message)

    if message and not message.get("isGroupMsg"):
        message_id = message.get("id")
        texto_usuario = message.get("body").strip().lower()
        agora = int(time.time())

        if texto_usuario in ["0", "voltar"]:
            contextos_usuario.pop(chat_id, None)
            contextos_usuario[chat_id] = {"ultimo_menu": agora}
            client.reply(chat_id, "Você voltou ao menu principal.\n\n" + menu_msg, message_id)
            return

        if texto_usuario in ["4", "obrigado"]:
            contextos_usuario.pop(chat_id, None)
            client.reply(chat_id, "Encerrando atendimento. Até logo! 👋", message_id)
            return

        contexto = contextos_usuario.get(chat_id, {})

        if "setor" not in contexto:
            ultimo_menu = contexto.get("ultimo_menu")
            tempo_passado = (agora - ultimo_menu) if ultimo_menu else None

            if texto_usuario in respostas_fixas:
                contextos_usuario[chat_id] = {
                    "setor": texto_usuario,
                    "em_conversa": False
                }
                client.reply(chat_id, respostas_fixas[texto_usuario] + "\n\nDigite sua dúvida ou escreva *0* para retornar ao menu.", message_id)
                return

            if not ultimo_menu or tempo_passado >= 43200:#enviar o menu 12 horas depois
                contextos_usuario[chat_id] = {
                    "ultimo_menu": agora
                }
                client.reply(chat_id, menu_msg, message_id)
            else:
                print(f"⏱ Menu não reenviado. Apenas {tempo_passado // 60} min desde o último envio.")
        else:
            if not contexto.get("em_conversa"):
                setor = contexto.get("setor")
                if setor == "1":
                    resposta = "📌 Atendimento Pier (Life):\n Sua mensagem foi registrada. Um atendente responderá em breve."
                elif setor == "2":
                    resposta = "📌 Atendimento Arthur (Benvita): \n Sua mensagem foi registrada. Um atendente responderá em breve."
                elif setor == "3":
                    resposta = "📌 Informática: Sua solicitação foi registrada. Um técnico responderá em breve."
                else:
                    resposta = "Opção inválida. Por favor, digite *0* para voltar ao menu."
                contextos_usuario[chat_id]["em_conversa"] = True
                client.reply(chat_id, resposta + "\n\n(_Digite *0* para retornar ao menu._)", message_id)
            else:
                print(f"💬 [{chat_id}] Mensagem do usuário em conversa: {texto_usuario}")

creator.client.onMessage(new_message)

print("🤖 Bot do WhatsApp está rodando...")

while True:
    time.sleep(1)
