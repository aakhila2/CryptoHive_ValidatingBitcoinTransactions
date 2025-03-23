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

# Generate three Legacy (P2PKH) addresses: A, B, and C
address_A = rpc_connection.getnewaddress("", "legacy")
address_B = rpc_connection.getnewaddress("", "legacy")
address_C = rpc_connection.getnewaddress("", "legacy")

print(f"📌 Legacy Addresses Generated:")
print(f"  - A (P2PKH): {address_A}")
print(f"  - B (P2PKH): {address_B}")
print(f"  - C (P2PKH): {address_C}")

# Fund Address A with 10 BTC
balance = rpc_connection.getbalance()
print(f"💰 Current Wallet Balance: {balance} BTC")

if balance < 10:
    print("❌ Insufficient funds! Please add more BTC.")
    exit()

txid_fund_A = rpc_connection.sendtoaddress(address_A, 10)
print(f"✅ Sent 10 BTC to A (TXID: {txid_fund_A})")

# Mine a block to confirm the transaction (This is for testnet, for mainnet you can skip or use other methods)
mining_address = rpc_connection.getnewaddress()
rpc_connection.generatetoaddress(1, mining_address)  # Generate a block to confirm the transaction
print()

#  Get UTXO (Unspent Transaction Output) for Address A'
utxos = rpc_connection.listunspent(1, 9999999, [address_A])
if not utxos:
    print("❌ No UTXOs available for Address A. Exiting.")
    exit()
    
# Print the UTXO details for Address A
print(f"🔍 UTXO details for Address A:")
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
    

    
    # If you need to analyze the script in more detail, you can split or parse it further if needed.
    print()

utxo = utxos[0]  # Use the first UTXO for the transaction
txid = utxo['txid']
vout = utxo['vout']
amount = utxo['amount']

#  Create a raw transaction from A → B with fee deduction
fee = Decimal("0.0001")  # Define a small fee for the transaction
outputs = {address_B: amount - fee}  # Deduct a small fee for the transaction


# Create raw transaction for A → B
raw_tx = rpc_connection.createrawtransaction([{"txid": txid, "vout": vout}], outputs)

# 5. Sign the raw transaction using the wallet
signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx)

# Decode the signed transaction for inspection
decoded_raw_tx = rpc_connection.decoderawtransaction(signed_tx['hex'])

# Ensure decoding process and print the details clearly
print(f"\n🔎 Decoded Raw Transaction A → B:")
if decoded_raw_tx:
    for key, value in decoded_raw_tx.items():
        print(f"  - {key}: {value}")
else:
    print("❌ Failed to decode the transaction.")

# Legacy script validation (P2PKH)
script_pubkey = decoded_raw_tx.get('vout', [{}])[0].get('scriptPubKey', {}).get('asm', '')

# Check for a P2PKH format by looking for the specific opcodes
if "OP_DUP OP_HASH160" in script_pubkey and "OP_EQUALVERIFY OP_CHECKSIG" in script_pubkey:
    print("✅ Legacy P2PKH script for A → B is properly formatted.")
else:
    print("⚠ Warning: The script does not follow the expected P2PKH format.")


# 6. Broadcast the signed transaction with retry mechanism
retry_count = 3
for attempt in range(retry_count):
    try:
        broadcast_txid = rpc_connection.sendrawtransaction(signed_tx['hex'])
        rpc_connection.generatetoaddress(1, mining_address)  # Generate a block to confirm the transaction

        print(f"\n✅ Transaction A → B broadcasted successfully!")
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

# Save the generated addresses to a text file
with open("generated_addresses.txt", "w") as f:
    f.write(f"Address A (P2PKH): {address_A}\n")
    f.write(f"Address B (P2PKH): {address_B}\n")
    f.write(f"Address C (P2PKH): {address_C}\n")

print("📄 Generated addresses saved to 'generated_addresses.txt'.")

print("\n✅ All transactions completed successfully!")