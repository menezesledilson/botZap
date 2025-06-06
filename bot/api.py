from flask import Flask, request, jsonify
from flask_cors import CORS
from db import init_db, adicionar_contato, remover_contato, listar_contatos, numero_bloqueado

app = Flask(__name__)
CORS(app)
init_db()

@app.route('/contatos', methods=['GET'])
def get_contatos():
    contatos = listar_contatos()
    return jsonify([{"nome": nome, "numero": numero} for nome, numero in contatos])

@app.route('/add-contato', methods=['POST'])
def add_contato():
    data = request.get_json()
    nome = data.get("nome")
    numero = data.get("numero")

    if nome and numero:
        nome_existente = numero_bloqueado(numero)
        if nome_existente:
            return jsonify({
                "erro": "contato já existe",
                "nome": nome_existente,
                "numero": numero  # mantém o formato enviado
            }), 409

        adicionar_contato(nome, numero)
        return jsonify({"status": "contato adicionado"}), 201

    return jsonify({"erro": "Dados inválidos"}), 400


@app.route('/contato', methods=['DELETE'])
def delete_contato():
    data = request.get_json()
    numero = data.get("numero")
    if numero:
        remover_contato(numero)
        return jsonify({"status": "contato removido"}), 200
    return jsonify({"erro": "Número não informado"}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)
