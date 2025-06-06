import re
import sqlite3

DB_PATH = "banco/contatos.db"

# Conexão global, permite acesso por múltiplas threads
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contatos_proibidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            numero TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()

def adicionar_contato(nome, numero):
    cur = conn.cursor()
    cur.execute("INSERT INTO contatos_proibidos (nome, numero) VALUES (?, ?)", (nome.strip(), numero.strip()))
    conn.commit()

def remover_contato(numero):
    numero = ''.join(filter(str.isdigit, numero))  # normaliza
    cur = conn.cursor()
    cur.execute("DELETE FROM contatos_proibidos WHERE numero = ?", (numero,))
    conn.commit()

def listar_contatos():
    cur = conn.cursor()
    cur.execute("SELECT nome, numero FROM contatos_proibidos")
    contatos = cur.fetchall()
    return contatos

def numero_bloqueado(numero):
    numero = ''.join(filter(str.isdigit, numero))  # normaliza
    cur = conn.cursor()
    cur.execute("SELECT nome FROM contatos_proibidos WHERE numero = ?", (numero,))
    resultado = cur.fetchone()
    return resultado[0] if resultado else None

def normalizar_numeros_do_banco():
    cur = conn.cursor()
    cur.execute("SELECT id, numero FROM contatos_proibidos")
    contatos = cur.fetchall()

    for id_contato, numero_original in contatos:
        numero_normalizado = re.sub(r'\D', '', numero_original)
        cur.execute("UPDATE contatos_proibidos SET numero = ? WHERE id = ?", (numero_normalizado, id_contato))

    conn.commit()
    print("📦 Todos os números foram normalizados com sucesso no banco.")
