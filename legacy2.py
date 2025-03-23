from bitcoinrpc.authproxy import AuthServiceProxy
from decimal import Decimal
import time
import random

# Bitcoin RPC connection settings
RPC_USER = "sunitha_parimi"
RPC_PASSWORD = "Sunitha@2005"
RPC_HOST = "127.0.0.1"
RPC_PORT = "18443"

# Connect to Bitcoin Core RPC
rpc_connection = AuthServiceProxy(f"http://{RPC_USER}:{RPC_PASSWORD}@{RPC_HOST}:{RPC_PORT}")

# Wallet name
wallet_name = "sunitha_parimi"

# Check if the wallet exists
wallets = rpc_connection.listwallets()
if wallet_name in wallets:
    print(f"✅ Wallet '{wallet_name}' found. Loading wallet...")
    rpc_connection = AuthServiceProxy(f"http://{RPC_USER}:{RPC_PASSWORD}@{RPC_HOST}:{RPC_PORT}/wallet/{wallet_name}")
else:
    print(f"🚀 Wallet '{wallet_name}' not found. Creating a new wallet...")
    rpc_connection.createwallet(wallet_name)

import re

# Read the addresses from the file and clean them up
try:
    with open("generated_addresses.txt", "r") as f:
        addresses = f.read().splitlines()
        # Clean addresses if they contain extra text like "Address B (P2PKH):"
        addresses = [re.sub(r"^Address [A-C] \(P2PKH\): ", "", addr) for addr in addresses]
        
        if len(addresses) < 3:
            raise ValueError("Insufficient addresses in file.")
except Exception as e:
    print(f"Error reading addresses: {e}")
    # If the file is not found or has an issue, generate new addresses
    address_A = rpc_connection.getnewaddress("A", "legacy")
    address_B = rpc_connection.getnewaddress("B", "legacy")
    address_C = rpc_connection.getnewaddress("C", "legacy")

    # Write the new addresses to the file
    with open("generated_addresses.txt", "w") as f:
        f.write("\n".join([address_A, address_B, address_C]))

    addresses = [address_A, address_B, address_C]

# Now you have clean addresses without any labels
address_A, address_B, address_C = addresses



# Ensure mining_address is defined before using it
mining_address = rpc_connection.getnewaddress()

# Get UTXO for Address B'
utxos_B = rpc_connection.listunspent(1, 9999999, [address_B])  # Fetch UTXOs for address B
if not utxos_B:
    print("❌ No UTXOs available for Address B'. Exiting.")
    exit()

# Print the UTXO details for Address B'
print(f"🔍 UTXO details for Address B':")
for utxo in utxos_B:
    print(f"  - TXID: {utxo['txid']}")
    print(f"  - VOUT: {utxo['vout']}")
    print(f"  - Amount: {utxo['amount']} BTC")
    print(f"  - Address: {utxo['address']}")
    print(f"  - Confirmations: {utxo['confirmations']}")
    print(f"  - Redeem Script: {utxo.get('redeemScript', 'N/A')}")
    print(f"  - Spendable: {utxo['spendable']}")

    # Print the scriptPubKey as a string
    script_pubkey = utxo['scriptPubKey']
    print(f"  - Locking Script (ScriptPubKey): {script_pubkey}")

    # If you need to analyze the script in more detail, you can split or parse it further if needed.
    print()

# Get the first UTXO from B' to use
utxo_B = utxos_B[0]
txid_B = utxo_B['txid']
vout_B = utxo_B['vout']
amount_B = utxo_B['amount']

# Create a raw transaction from B → C with fee deduction
fee = Decimal("0.0001")  # Define a small fee for the transaction
outputs_B_to_C = {address_C: amount_B - fee}  # Deduct a small fee for the transaction

# Create raw transaction for B→ C
raw_tx_B_to_C = rpc_connection.createrawtransaction([{"txid": txid_B, "vout": vout_B}], outputs_B_to_C)

# Sign the raw transaction using the wallet
signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx_B_to_C)

# Decode the signed transaction for inspection
decoded_raw_tx = rpc_connection.decoderawtransaction(signed_tx['hex'])

# Ensure decoding process and print the details clearly
print(f"\n🔎 Decoded Raw Transaction B → C:")
if decoded_raw_tx:
    for key, value in decoded_raw_tx.items():
        print(f"  - {key}: {value}")
else:
    print("❌ Failed to decode the transaction.")

# Legacy script validation (P2PKH)
script_pubkey = decoded_raw_tx.get('vout', [{}])[0].get('scriptPubKey', {}).get('asm', '')

# Check for a P2PKH format by looking for the specific opcodes
if "OP_DUP OP_HASH160" in script_pubkey and "OP_EQUALVERIFY OP_CHECKSIG" in script_pubkey:
    print("✅ Legacy P2PKH script for B→ C is properly formatted.")
else:
    print("⚠ Warning: The script does not follow the expected P2PKH format.")
    
# Broadcast the signed transaction
retry_count = 3
for attempt in range(retry_count):
    try:
        broadcast_txid_B_to_C = rpc_connection.sendrawtransaction(signed_tx['hex'])
        rpc_connection.generatetoaddress(1, mining_address)  # Generate a block to confirm the transaction

        print(f"\n✅ Transaction B → C broadcasted successfully!")
        print(f"  - TXID: {broadcast_txid_B_to_C}")
        print(f"  - Amount: {amount_B - fee} BTC (Fee deducted: {fee} BTC)")

        # Wait for confirmation
        time.sleep(5)
        tx_info_B_to_C = rpc_connection.getrawtransaction(broadcast_txid_B_to_C, True)
        if tx_info_B_to_C.get('confirmations', 0) > 0:
            print("✅ Transaction has been confirmed!")
            break
        else:
            print("❌ Transaction not yet confirmed.")
            if attempt < retry_count - 1:
                print("🔄 Retrying...")
                time.sleep(random.randint(5, 15))  # Random delay before retry
    except Exception as e:
        print(f"❌ Failed to broadcast transaction: {e}")
        if attempt < retry_count - 1:
            print("🔄 Retrying...")
            time.sleep(random.randint(5, 15))  # Random delay before retry
        else:
            exit()
