import json
import logging
from flask import Flask, request, jsonify, abort
from web3 import Web3, HTTPProvider, Account
from web3.middleware import geth_poa_middleware
import hashlib
import configparser

# Carga la configuración desde el archivo
config = configparser.ConfigParser()
config.read('config.conf')

# Configuración inicial del logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Inicializa la aplicación Flask
app = Flask(__name__)

# Configuración de Web3
web3 = Web3(HTTPProvider(config['DEFAULT']['NodeURL']))  # Reemplaza con tu URL del nodo Ethereum
assert web3.is_connected()
web3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract_address = web3.to_checksum_address(config['DEFAULT']['ContractAddress'])
contract = web3.eth.contract(address=contract_address, abi=config['DEFAULT']['abi'])

@app.before_request
def before_request():

    token = request.headers.get('Authorization')

    if not token or token != 'Bearer '+config['DEFAULT']['API_TOKEN']:
        abort(401)  # No autorizado

@app.route('/pay_commissions', methods=['POST'])
def pay_commissions():
    try:
        data = request.json
        print(data)
        wallets = data.get('wallets')
        checksum_addresses = [Web3.to_checksum_address(address) for address in wallets]
        levelIds = data.get('levels')
        amount = data.get('amount')

        # Convertir el amount de Ether a Wei
        convert_amount = web3.to_wei(amount, 'mwei')

        # Obtener el nonce actual para la dirección del wallet
        nonce = web3.eth.get_transaction_count(config['DEFAULT']['WalletAddress'])
        gasprice = web3.eth.gas_price
        # Construye la transacción
        transaction = contract.functions.payCommision(checksum_addresses, levelIds, convert_amount).build_transaction({
            'from': Web3.to_checksum_address(config['DEFAULT']['WalletAddress']),
            'chainId': int(config['DEFAULT']['ChainId']),
            #'gasPrice': web3.to_wei(config['DEFAULT']['GasPrice'], 'gwei'),
            'gasPrice': gasprice, 
            'nonce': nonce,
            # 'type': '0x0'
        })

        # Firmar la transacción con la clave privada del wallet
        signed_txn = web3.eth.account.sign_transaction(transaction, config['DEFAULT']['WalletPrivateKey'])

        # Enviar la transacción firmada a la red de Ethereum
        txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(txn_hash)
        # Esperar a que la transacción sea minada
        txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
        transaction_hash = txn_receipt.logs[0]['transactionHash'].hex()
        # Devolver el recibo de la transacción como respuesta
        return jsonify(
            {'status': txn_receipt.status, 'transaction_hash': transaction_hash,
             'url': f'https://polygonscan.com/tx/' + transaction_hash}), 200

    except Exception as e:
        # Registra el error
        logging.error(f'Error processing request: {e}')

        # Devuelve un mensaje de error
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/add_level', methods=['POST'])
def add_level():
    data = request.json
    _id = data.get('id')
    _name = data.get('name')
    _percent = data.get('percent')
    nonce = web3.eth.get_transaction_count(config['DEFAULT']['WalletAddress'])

    tx = contract.functions.addLevel(_id, _name, _percent).build_transaction({
        'chainId': 137,
        # 'gas': 2000000,
        'gasPrice': web3.to_wei('139', 'gwei'),
        'nonce': nonce
    })

    signed_tx = web3.eth.account.sign_transaction(tx, config['DEFAULT']['WalletPrivateKey'])
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    txn_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return web3.to_hex(tx_hash), txn_receipt


@app.route('/getbalance', methods=['GET'])
def get_balance():
    balance = contract.functions.getBalanceContract().call()
    return jsonify(
        {'status': 'success', 'balance': balance}), 200


# Iniciar el servidor Flask si este archivo es el "main"
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
