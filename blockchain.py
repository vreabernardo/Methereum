import hashlib
import json
from os import replace
import subprocess
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from urllib.parse import urlparse
import requests as rq
import PySimpleGUI as sg

logo = sg.Image("logo.png")

layout = [
    [sg.Column([[logo]], justification='center')],
    [sg.Column([[sg.Text('Porta: ', size =(15, 1)), sg.InputText()],
    [sg.Submit(), sg.Cancel()]], justification='center')],
]

init = sg.Window("Bem vindo", layout)

event, values = init.read()

porta = values[1]

init.close()

open("porta.txt", "w").write(porta)

class Blockchain(object):
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        
        # genesis block
        self.new_block(previous_hash=1, proof=100)
    
    def porta(self):
        return porta
    
    def new_block(self, proof, previous_hash=None):
        """
        Cria um novo bloco na Blockchain
        :param proof: <int> Prova dada pelo algoritomo de PoW
        :param previous_hash: (Optional) <str> Hash do bloco anterior 
        :return: <dict> Novo Bloco
        
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Nova lista de transações
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Nova transação que vai para o proximo bloco minerado
        :param sender: <str> De:
        :param recipient: <str> Para:
        :param amount: <int> Valor
        :return: <int> O index do bloco para onde vai a transação
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1


    def register_node(self,address):
        """
        Add novo node para a lista de nodes
        :param address: <str> endereço do Node. Ex. 'http://localhost:5000'
        :return: None
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # só aceita endereços do estilo: '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def valid_chain(self,chain):
        
        """
        Validar um bloco
        :param chain: <list> blockchain
        :return: <bool> True se valido, Flase se invalido
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")

            # checar se a hash é legit
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            # checar se a PoW é legit
            if not self.valid_proof(last_block["proof"],block["proof"]):
                return False
            
            last_block = block
            current_index +=1
        return True
    
    def resolve_conflicts(self):
        """
        Este é o  Algoritmo de Consenso, ele resolve conflitos
        substituindo a nossa cadeia de transações pela mais longa na rede de nodes. O satoshi é que manda 
        :return: <bool> True se a cadeia foi substituida, False se não.
        """
        neighbours = self.nodes
        new_chain = None

        # max length da cadeia corrente
        max_length = len(self.chain)

        #  Ver todas as cadeias na rede de nodes
        for node in neighbours:
            url = "http://"+str(node)+"/chain"
            response = rq.get(url)
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()["chain"]

                # vereficar se a cadeia é legit e se é maior q a nossa
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Subsituir a nossa cadeia se encontrarmos uma legit e maior 
        if new_chain:
            self.chain = new_chain
            return True
        return False

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Cria a SHA-256 hash do bloco
        :param block: <dict> Bloco
        :return: <str>
        """

        # Temos q ter a certeza de que o dicionário está ordenado, ou vamos ter hashes inconsistentes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        
        """
        Proof of Work:
         - Encontre um número p' tal que hash(pp') contenha 4 zeros à esquerda, onde p é o p' anterior
         - p é a prova anterior e p' é a nova prova
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Valida a prova: hash(last_proof, proof) contém 4 zeros à esquerda
        :param last_proof: <int> Prova anterior 
        :param proof: <int> Prova atual
        :return: <bool> True se sim, False se não.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
    def create_wallet():
        return str(uuid4()).replace('-', '')

        


"""
endpoints

    /transactions/new     criar uma nova transação para um bloco.
    /mine                 minerar outro bloco.
    /chain                ver transações.

"""


#Node

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

#Endereço do node

node_identifier = str(uuid4()).replace('-', '')

# Inicia a Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():

    rq.get("http://localhost:"+str(porta)+"/nodes/resolve")

    # Rodar PoW para obter a proxima prova
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # premio de mineração.
    # De "0" pois é um premio de mineração
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # criar novo bloco
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return json.dumps(response, sort_keys=True, indent=4), 200
  

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # POST completo
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Valores em falta', 400

    # Criar nova transação
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'A trasação realizada com sucesso: Bloco {index}'}
    return json.dumps(response, sort_keys=True, indent=4), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return json.dumps(response, sort_keys=True, indent=4), 200



@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    
    values = request.get_json()
    nodes = values.get("nodes")
    
    if nodes is  None:
        return "Erro ao adicinar Node "+str(nodes),400
    
    for node in nodes:
        blockchain.register_node(node)
    response = {
        "message" : "Novo node foi adicionado à pool",
        "total nodes" : list(blockchain.nodes),
    }
    return json.dumps(response, sort_keys=True, indent=4), 201

@app.route('/nodes/resolve', methods=['GET'])
def concensus():

    try:
        replaced = blockchain.resolve_conflicts()

        if replaced:
            response = {
                "message" : "A corrente foi atualizada",
                "new chain": blockchain.chain
            }

        else:
            response = {
                "message" : "A corrente está atualizada'",
                "new chain": blockchain.chain
            }
    
        return json.dumps(response, sort_keys=True, indent=4), 201
    except:
        response = {
                "message" : "erro a comunicar com os outros nodes'",
                "new chain": blockchain.chain
            }
        return json.dumps(response, sort_keys=True, indent=4), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=porta)
