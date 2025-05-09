# Validating Bitcoin Transactions

## Team Details 

Team Name : **CryptoHive**

Team Members : 
- Akella Akhila, 230001005, CSE
- Kommireddy Jayanthi, 230001041, CSE
- Parimi Sunitha, 230001061, CSE

## Introduction
This project contains three Python scripts that interact with a Bitcoin RPC node using the `bitcoinrpc` library. The scripts perform various operations such as wallet loading, address generation, UTXO handling, raw transaction creation, signing, and broadcasting. The main tasks of each script include working with different address types (Legacy, SegWit) and performing Bitcoin transactions on the Testnet.

## Requirements 
Before running the scripts, ensure you have the following:

- Python 3.x installed
- Bitcoin Core running with RPC enabled on the Testnet or Mainnet
- `bitcoinrpc` Python library (`pip install python-bitcoinrpc`)

## Bitcoin Core Configuration
You need to have Bitcoin Core set up on your machine, and the configuration should look something like this in `bitcoin.conf` (usually located in the Bitcoin data directory):

testnet=1 rpcuser=--username-- rpcpassword=--password-- rpcallowip=127.0.0.1 rpcport=18443

Make sure the RPC settings match the ones in the script (username, password, host, and port).


## Instructions

### Running the scripts
1. Clone the repository, Install dependencies, Update configuration
2. Run the bash codes :
   - python legacy1.py
   - python legacy2.py
   - python segwit.py
3. Expected outputs : Each script will print the following outputs
   - status of wallet creation or loading
   - generated address (legacy or segwit)
   - balance of wallet
   - TX details, including TXID
   - information on UTXOs
   - signed TX details
   - whether TX was successfully broadcasted or not
4. The addresses generated by script (legacy/ segwit) are saved to a file called generated_address.txt
