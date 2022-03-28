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
        
        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)
    
    def porta(self):
        return porta
    
    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1


    def register_node(self,address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://localhost:5000'
        :return: None
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def valid_chain(self,chain):
        
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")

            # check if the hash of the block is legit
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            # check if the PoW is legit
            if not self.valid_proof(last_block["proof"],block["proof"]):
                return False
            
            last_block = block
            current_index +=1
        return True
    
    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """
        neighbours = self.nodes
        new_chain = None

        # We want a chain bigger than ours
        max_length = len(self.chain)

        #  Grab and verify the chains from all the nodes is our network
        for node in neighbours:
            url = "http://"+str(node)+"/chain"
            response = rq.get(url)
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()["chain"]

                # Check if the lenght is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
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
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
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
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
    def create_wallet():
        return str(uuid4()).replace('-', '')

        


"""
endpoints

    /transactions/new     create a new transaction to a block
    /mine                 tell our server to mine a new block.
    /chain                return the full Blockchain.

"""


#Node

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Generate a globally unique address for this node and wallet

node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():

    rq.get("http://localhost:"+str(porta)+"/nodes/resolve")

    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
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

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
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
        return "Error Please supply a valid list of nodes "+str(nodes),400
    
    for node in nodes:
        blockchain.register_node(node)
    response = {
        "message" : "New nodes have been added",
        "total nodes" : list(blockchain.nodes),
    }
    return json.dumps(response, sort_keys=True, indent=4), 201

@app.route('/nodes/resolve', methods=['GET'])
def concensus():

    try:
        replaced = blockchain.resolve_conflicts()

        if replaced:
            response = {
                "message" : "Our Chain was replaced",
                "new chain": blockchain.chain
            }

        else:
            response = {
                "message" : "Our chain is authoritative'",
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