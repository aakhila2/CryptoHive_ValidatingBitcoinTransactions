from bitcoinrpc.authproxy import AuthServiceProxy
from decimal import Decimal
import time
import random

# Bitcoin RPC connection settings
RPC_USER = "sunitha_parimi"
RPC_PASSWORD = "Sunitha@2005"
RPC_HOST = "127.0.0.1"
RPC_PORT = "18443"

# Establish connection to bitcoind RPC
rpc_connection = AuthServiceProxy(f"http://{RPC_USER}:{RPC_PASSWORD}@{RPC_HOST}:{RPC_PORT}")

# Wallet name you want to load or create
wallet_name = "sunitha_parimi"

# Check if the wallet exists
wallets = rpc_connection.listwallets()

if wallet_name in wallets:
    print(f"Wallet '{wallet_name}' found. Loading the wallet...")
    rpc_connection = AuthServiceProxy(f"http://{RPC_USER}:{RPC_PASSWORD}@{RPC_HOST}:{RPC_PORT}/wallet/{wallet_name}")
else:
    print(f"Wallet '{wallet_name}' not found. Creating a new wallet...")
    rpc_connection.createwallet(wallet_name)

# List wallets to verify the new wallet was created or loaded
wallets = rpc_connection.listwallets()
print(f"Loaded wallets: {wallets}")
print()

# 1. Generate three P2SH-SegWit addresses: A', B', and C'
address_A_seg = rpc_connection.getnewaddress("", "p2sh-segwit")
address_B_seg = rpc_connection.getnewaddress("", "p2sh-segwit")
address_C_seg = rpc_connection.getnewaddress("", "p2sh-segwit")

# Display generated P2SH-SegWit addresses
print(f"🛠 SegWit Addresses Generated:")
print(f"  - A' (P2SH-P2WPKH): {address_A_seg}")
print(f"  - B' (P2SH-P2WPKH): {address_B_seg}")
print(f"  - C' (P2SH-P2WPKH): {address_C_seg}")
print()

# 2. Fund Address A' with 10 BTC (or any other amount you want)
balance = rpc_connection.getbalance()
print(f"Current wallet balance: {balance} BTC")

if balance < 10:
    print("❌ Insufficient funds. Exiting.")
    exit()

print("🔄 Funding A' with 10 BTC...")
txid_seg = rpc_connection.sendtoaddress(address_A_seg, 10)

if not txid_seg:
    print("❌ Failed to send Bitcoin to Address A'. Exiting.")
    exit()

print(f"Sent 10 BTC to A' with TXID: {txid_seg}")

# Mine a block to confirm the transaction (This is for testnet, for mainnet you can skip or use other methods)
mining_address = rpc_connection.getnewaddress()
rpc_connection.generatetoaddress(1, mining_address)  # Generate a block to confirm the transaction
print()

# 3. Get UTXO (Unspent Transaction Output) for Address A'
utxos = rpc_connection.listunspent(1, 9999999, [address_A_seg])
if not utxos:
    print("❌ No UTXOs available for Address A'. Exiting.")
    exit()

# Print the UTXO details for Address A'
print(f"🔍 UTXO details for Address A':")
for utxo in utxos:
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
    
    # Analyzing the challenge scripts (scriptSig) for more details
    print(f"  - ScriptSig analysis: {utxo.get('scriptSig', 'N/A')}")
    
    # If you need to analyze the script in more detail, you can split or parse it further if needed.
    print()

utxo = utxos[0]  # Use the first UTXO for the transaction
txid = utxo['txid']
vout = utxo['vout']
amount = utxo['amount']

# 4. Create a raw transaction from A' → B' with fee deduction
fee = Decimal("0.0001")  # Define a small fee for the transaction
outputs = {address_B_seg: amount - fee}  # Deduct a small fee for the transaction

# Create raw transaction for A' → B'
raw_tx = rpc_connection.createrawtransaction([{"txid": txid, "vout": vout}], outputs)

# 5. Sign the raw transaction using the wallet
signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx)

# Decode the signed transaction for inspection
decoded_raw_tx = rpc_connection.decoderawtransaction(signed_tx['hex'])

# Ensure decoding process and print the details clearly
print(f"\n🔎 Decoded Raw Transaction A' → B':")
if decoded_raw_tx:
    for key, value in decoded_raw_tx.items():
        print(f"  - {key}: {value}")
else:
    print("❌ Failed to decode the transaction.")

# SegWit script validation
script_pubkey = decoded_raw_tx.get('vout', [{}])[0].get('scriptPubKey', {}).get('asm', '')
if "OP_CHECKMULTISIG" in script_pubkey:
    print("⚠ Warning: ScriptPubKey contains OP_CHECKMULTISIG, SegWit may not be valid.")
else:
    print("✅ SegWit script for A'→ B' is properly formatted.")

# 6. Broadcast the signed transaction with retry mechanism
retry_count = 3
for attempt in range(retry_count):
    try:
        broadcast_txid = rpc_connection.sendrawtransaction(signed_tx['hex'])
        rpc_connection.generatetoaddress(1, mining_address)  # Generate a block to confirm the transaction

        print(f"\n✅ Transaction A' → B' broadcasted successfully!")
        print(f"  - TXID: {broadcast_txid}")
        print(f"  - Amount: {amount - fee} BTC (Fee deducted: {fee} BTC)")

        # Ensure the transaction is included in a mined block
        print(f"⏳ Waiting for confirmation...")
        time.sleep(5)  # Wait for some time to confirm

        # Check for confirmation in the blockchain
        tx_info = rpc_connection.getrawtransaction(broadcast_txid, True)
        if tx_info.get('confirmations', 0) > 0:
            print("✅ Transaction has been confirmed!")
            print()
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

# 7. Now create a Transaction from Address B' → Address C'
# Get UTXO for Address B'
utxos_B = rpc_connection.listunspent(1, 9999999, [address_B_seg])
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

    # Analyzing the challenge scripts (scriptSig) for more details
    print(f"  - ScriptSig analysis: {utxo.get('scriptSig', 'N/A')}")

    # If you need to analyze the script in more detail, you can split or parse it further if needed.
    print()

# Get the first UTXO from B' to use
utxo_B = utxos_B[0]
txid_B = utxo_B['txid']
vout_B = utxo_B['vout']
amount_B = utxo_B['amount']

# Create a raw transaction from B' → C'
outputs_B_to_C = {address_C_seg: amount_B - fee}  # Deduct a small fee for the transaction

# Create raw transaction for B' → C'
raw_tx_B_to_C = rpc_connection.createrawtransaction([{"txid": txid_B, "vout": vout_B}], outputs_B_to_C)

# Sign the raw transaction using the wallet
signed_tx_B_to_C = rpc_connection.signrawtransactionwithwallet(raw_tx_B_to_C)

# Decode the signed transaction for inspection
decoded_raw_tx = rpc_connection.decoderawtransaction(signed_tx['hex'])

# Ensure decoding process and print the details clearly
print(f"\n🔎 Decoded Raw Transaction B' → C':")
if decoded_raw_tx:
    for key, value in decoded_raw_tx.items():
        print(f"  - {key}: {value}")
else:
    print("❌ Failed to decode the transaction.")

# SegWit script validation
script_pubkey = decoded_raw_tx.get('vout', [{}])[0].get('scriptPubKey', {}).get('asm', '')
if "OP_CHECKMULTISIG" in script_pubkey:
    print("⚠ Warning: ScriptPubKey contains OP_CHECKMULTISIG, SegWit may not be valid.")
else:
    print("✅ SegWit script for B'→ C' is properly formatted.")
    
# Broadcast the signed transaction
retry_count = 3
for attempt in range(retry_count):
    try:
        broadcast_txid_B_to_C = rpc_connection.sendrawtransaction(signed_tx_B_to_C['hex'])
        rpc_connection.generatetoaddress(1, mining_address)  # Generate a block to confirm the transaction

        print(f"\n✅ Transaction B' → C' broadcasted successfully!")
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