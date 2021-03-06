from flask import Flask, jsonify, request
from src.node import btc
from src import services
from src.routers.v2 import v2_router
from src.routers.v3 import v3_router
from src.rpc.es_send import send_exception_to_kibana
from src.services.v3.is_demon_alive import is_demon_alive
from src.services.v3.is_node_alive import is_node_alive

app = Flask(__name__)


@app.route('/', methods=['GET'])
def is_connected():
    return jsonify({'message': True})


@app.route('/is-demon-alive', methods=['GET'])
def is_demon_alive_route():
    try:
        return jsonify({'message': is_demon_alive()})
    except Exception as e:
        send_exception_to_kibana(e, 'IS NODE DEAD')
        return jsonify({'message': False})


@app.route('/is-node-alive', methods=['GET'])
def is_connected_to_node():
    try:
        return jsonify({'message': is_node_alive()})
    except Exception as e:
        send_exception_to_kibana(e, 'IS NODE DEAD')
        return jsonify({'message': False})


@app.route('/documentation', methods=['POST', 'GET'])
def doc():
    """Documentation"""
    if request.method == 'GET':
        return jsonify({'doc': {
            'create_wallet': ['POST', '/create-wallet'],
            'create_deterministic_wallet': ['POST', '/create-deterministic-wallet'],
            'get_balance': ['GET', '/get-balance'],
            'get_received': ['GET', '/get-received'],
            'get_send': ['GET', '/get-send'],
            'create_transaction': ['POST', '/create-transaction'],
            'sign_and_send_transaction': ['POST', '/sign-send-transaction'],
            'get_all_transactions': ['GET', '/get-all-transactions'],
            'get_optimal_fees': ['GET', '/get-fee'],
            'get_unspent': ['GET', '/get-unspent']
        }})
    else:
        return jsonify({'error': 'Use a "GET" request'})


@app.route('/create-wallet', methods=['POST', 'GET'])
def create_wallet():
    """ This method creates a BTC wallet """
    if request.method == 'POST':
        if not request.json or 'words' not in request.json:
            return jsonify(btc.create_wallet())
        return jsonify(btc.create_wallet(words=request.json['words']))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@app.route('/create-deterministic-wallet', methods=['POST', 'GET'])
def create_deterministic_wallet():
    """ This method creates a BTC deterministic wallet """
    if request.method == 'POST':
        if not request.json:
            return jsonify(btc.create_deterministic_wallet())
        if "words" in request.json:
            return jsonify(btc.create_deterministic_wallet(words=request.json['words']))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@app.route('/get-balance', methods=['POST', 'GET'])
def get_balance():
    """ Check your wallet balance """
    if request.method == 'POST':
        if not request.json or 'privateKey' not in request.json:
            return jsonify({'error': 'The argument "privateKey" was not found'})
        return jsonify(btc.get_balance(private_key=request.json['privateKey']))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@app.route('/get-received', methods=['POST', 'GET'])
def get_received():
    """ Get all received bitcoins """
    if request.method == 'POST':
        if not request.json or 'address' not in request.json:
            return jsonify({'error': 'The argument "address" was not found'})
        return jsonify(btc.get_receipt_at_address(request.json['address']))
    else:
        return jsonify({'error': 'Use a "GET" request'})


@app.route('/get-send', methods=['POST', 'GET'])
def get_send():
    """ Receive all sent bitcoins """
    if request.method == "POST":
        if not request.json or "address" not in request.json:
            return jsonify({"error": 'The argument "address" was not found'})
        return jsonify(btc.get_sent_at_address(request.json['address']))
    else:
        return jsonify({'error': 'Use a "GET" request'})


@app.route('/create-transaction-service', methods=['POST', 'GET'])
def create_transaction_service():
    """Create transaction without sign, but with fee"""
    if request.method == 'POST':
        if "fromAddress" not in request.json:
            return jsonify({'error': 'The argument "fromAddress" was not found'})
        if "outputs" not in request.json:
            return jsonify({'error': 'The argument "outputs" was not found'})
        if "privateKey" not in request.json:
            return jsonify({'error': 'The argument "privateKey" was not found'})
        if "adminAddress" not in request.json:
            return jsonify({'error': 'The argument "adminAddress" was not found'})
        if "adminFee" not in request.json:
            return jsonify({'error': 'The argument "adminFee" was not found'})

        a = services.create_transaction(
            from_address=request.json['fromAddress'],
            outputs=request.json['outputs'],
            private_key=request.json['privateKey'],
            admin_wallet=request.json['adminAddress'],
            admin_fee=request.json['adminFee']
        )
        return jsonify(a)
    else:
        return jsonify({'error': 'Use a "POST" request'})


@app.route('/create-transaction', methods=['POST', 'GET'])
def create_transaction():
    """Create transaction without sign, but with fee"""
    if request.method == 'POST':
        if "fromAddress" not in request.json:
            return jsonify({'error': 'The argument "fromAddress" was not found'})
        if "outputs" not in request.json:
            return jsonify({'error': 'The argument "outputs" was not found'})
        if "privateKey" not in request.json:
            return jsonify({'error': 'The argument "privateKey" was not found'})
        a = services.create_transaction(
            from_address=request.json['fromAddress'],
            outputs=request.json['outputs'],
            private_key=request.json['privateKey'],
        )
        return jsonify(a)
    else:
        return jsonify({'error': 'Use a "POST" request'})


@app.route('/sign-send-transaction', methods=['POST', 'GET'])
def sign_and_send_transaction():
    """Sign and send a transaction"""
    if request.method == 'POST':
        if not request.json or "privateKeys" not in request.json:
            return jsonify({'error': 'The argument "privateKeys" was not found'})
        if "createTxHex" not in request.json:
            return jsonify({'error': 'The argument "createTxHex" was not found'})
        if "maxFeeRate" not in request.json:
            return jsonify({'error': 'The argument "maxFeeRate" was not found'})
        tx = btc.sign_and_send_transaction(
            private_keys=request.json["privateKeys"],
            create_tx_hex=request.json["createTxHex"],
            max_fee_rate=request.json["maxFeeRate"]
        )
        return jsonify(tx)
    else:
        return jsonify({'error': 'Use a "POST" request'})


@app.route('/get-all-transactions', methods=['POST', 'GET'])
def get_all_transactions():
    """ This router will return all transactions of the transferred address\addresses """
    if request.method == 'POST':
        if not request.json or "addresses" not in request.json:
            return jsonify({'error': 'The argument "addresses" was not found'})
        return jsonify(btc.get_all_transactions(addresses=request.json["addresses"]))
    else:
        return jsonify({'error': 'Use a "GET" request'})


@app.route('/get-optimal-fee', methods=['POST', 'GET'])
def get_optimal_fees():
    if request.method == 'POST':
        if not request.json:
            return jsonify(btc.get_optimal_fees())
        if "input" not in request.json:
            return jsonify({'error': 'The argument "input" was not found'})
        if "output" not in request.json:
            return jsonify({'error': 'The argument "output" was not found'})
        if "toConfirmWithin" not in request.json:
            return jsonify({'error': 'The argument "toConfirmWithin" was not found'})

        return jsonify(btc.get_optimal_fees(
            from_=request.json["input"],
            to_=request.json["output"],
            to_confirm_within=request.json["toConfirmWithin"]
        ))
    else:
        return jsonify({'error': 'Use a "POST" request'})


@app.route('/get-unspent', methods=['POST', 'GET'])
def get_unspent():
    """Get unspent transactions"""
    if request.method == 'POST':
        if not request.json or "address" not in request.json:
            return jsonify({'error': 'The argument "address" was not found'})
        return jsonify(btc.get_unspent(address=request.json["address"]))
    else:
        return jsonify({'error': 'Use a "GET" request'})


app.register_blueprint(v2_router, url_prefix='/v2')
app.register_blueprint(v3_router, url_prefix='/v3')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
