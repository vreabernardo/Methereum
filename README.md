<p align="center">
    <img width=25% src="https://github.com/vreabernardo/Methereum/assets/45080358/7c24f2f0-fb68-495a-a524-fe2ef337a3c2">
</p>


<p align="center">
<h1 align="center"> SuperCoin </h1>
<h3 align="center"> This is a simple implementation of a Blockchain and a wallet client compatible with multiple node usage in Python 3.</h3>

## Getting Started

### Dependencies
The following dependencies are required to run the project:
- PySimpleGUI
- Flask
- qrcode
- pillow

You can install them easily via `pip` using the following command:
```bash
pip install PySimpleGUI Flask qrcode pillow
```

### Installation
To get started, clone the repository by running the following command in your desired directory:
```bash
git clone https://github.com/vreaw/Methereum.git
```

After cloning the repository, navigate to the project directory:
```bash
cd Methereum
```

### Starting the Blockchain
To start the blockchain, run the following command:
```bash
python3 blockchain.py
```
You will then be prompted to choose a port number for your node to operate on.

Once you have selected a port, everything will be set in motion, and you can proceed to launch the wallet client.

### Running the Client
To run the client, execute the following command:
```bash
python3 client.py
```
The client is now ready to use.

<p align="center">
    <img width=60% src="https://user-images.githubusercontent.com/45080358/179635917-2bee1828-40d7-4a16-b874-477cde67e041.png">
</p>

## Code Documentation

The code is documented using inline comments to explain the purpose and functionality of each section. Below is an overview of the main components:

### Blockchain Class

#### `new_block(proof, previous_hash=None)`
Creates a new block in the blockchain with the given proof and optional previous hash.

#### `new_transaction(sender, recipient, amount)`
Adds a new transaction to the current block.

#### `register_node(address)`
Adds a new node to the list of nodes.

#### `valid_chain(chain)`
Validates a chain of blocks to ensure its integrity.

#### `resolve_conflicts()`
Resolves conflicts between different nodes by replacing the current chain with the longest valid chain in the network.

#### `last_block`
Returns the last block in the chain.

#### `hash(block)`
Calculates the SHA-256 hash of a block.

#### `proof_of_work(last_proof)`
Performs the proof-of-work algorithm to find the next valid proof.

#### `valid_proof(last_proof, proof)`
Validates a proof by checking if it meets the required criteria.

### Flask Endpoints

#### `/mine`
GET request to mine a new block.

#### `/transactions/new`
POST request to create a new transaction.

#### `/chain`
GET request to view the full blockchain.

#### `/nodes/register`
POST request to register new nodes.

#### `/nodes/resolve`
GET request to resolve conflicts and update the blockchain.

### Wallet Creation

The code includes a `create_wallet()` function that generates a new wallet address using the UUIDv4 format. This function can be used to create unique wallet addresses for users.
