from flask import Flask, request, jsonify
from inserir import insert_funcionarios
from consultar import read_funcionarios
from atualizar import update_funcionarios
from deletar import delete_funcionarios

app = Flask(__name__)

@app.route('/funcionarios', methods=['POST'])
def criar_funcionario():
    dados = request.json
    print('API', dados)
    resposta = insert_funcionarios(dados)
    return jsonify(resposta), 201 if resposta.get('status') == 'sucesso' else 400

@app.route('/funcionarios', methods=['GET'])
def listar_funcionarios():
    resposta = read_funcionarios()
    return jsonify(resposta)

@app.route('/funcionarios/<int:funcionario_id>', methods=['PUT'])
def atualizar_funcionario(funcionario_id):
    dados = request.json
    dados['funcionario_id'] = funcionario_id
    resposta = update_funcionarios(dados)
    return jsonify(resposta), 200 if resposta.get('status') == 'sucesso' else 400

@app.route('/funcionarios/<int:funcionario_id>', methods=['DELETE'])
def excluir_funcionario(funcionario_id):
    resposta = delete_funcionarios(funcionario_id)
    return jsonify(resposta)

app.run(debug=True)
