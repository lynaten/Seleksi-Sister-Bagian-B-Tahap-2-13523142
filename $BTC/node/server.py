from flask import Flask, request, jsonify
from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction
from blockchain.block import Block
from blockchain.exceptions import BlockchainError, TransactionError, InvalidPreviousHash, InvalidBlockHash, InvalidProofOfWork
import argparse
import requests

def create_app(difficulty=4):
    app = Flask(__name__)
    app.config["blockchain"] = Blockchain(difficulty=difficulty)
    app.config["peers"] = set()

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Fallback handler untuk semua exception"""
        if isinstance(e, (BlockchainError, TransactionError)):
            return jsonify({"error": str(e)}), 400
        # kalau error generic, log dan kasih 500
        print(f"🔥 Internal server error: {e}")
        return jsonify({"error": "Internal server error"}), 500

    @app.route('/transaction', methods=['POST'])
    def add_transaction():
        blockchain = app.config["blockchain"]
        try:
            data = request.get_json()
            if not data or "sender" not in data or "recipient" not in data or "amount" not in data:
                raise TransactionError("Missing transaction fields")
            tx = Transaction(data['sender'], data['recipient'], data['amount'])
            blockchain.add_transaction(tx.to_dict())
            return jsonify({"message": "Transaction added"}), 201
        except TransactionError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/mine', methods=['GET'])
    def mine():
        blockchain = app.config["blockchain"]
        peers = app.config["peers"]
        try:
            block = blockchain.mine_block()
            if not block:
                return jsonify({"message": "No transactions to mine"}), 200

            for peer in peers:
                try:
                    requests.post(f"{peer}/receive_block", json=block.to_dict())
                except Exception as e:
                    print(f"⚠️ Broadcast gagal ke {peer}: {e}")
            return jsonify(block.to_dict()), 200
        except BlockchainError as e:
            return jsonify({"error": str(e)}), 400


    @app.route('/mine_local', methods=['GET'])
    def mine_local():
        blockchain = app.config["blockchain"]
        try:
            block = blockchain.mine_block()
            if not block:
                return jsonify({"message": "No transactions to mine"}), 200
            return jsonify(block.to_dict()), 200
        except BlockchainError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/broadcast_block', methods=['POST'])
    def broadcast_block():
        blockchain = app.config["blockchain"]
        peers = app.config["peers"]
        try:
            last_block = blockchain.get_last_block()
            for peer in peers:
                try:
                    requests.post(f"{peer}/receive_block", json=last_block.to_dict())
                except Exception as e:
                    print(f"⚠️ Broadcast gagal ke {peer}: {e}")
            return jsonify({"message": "Broadcasted", "block": last_block.to_dict()}), 200
        except BlockchainError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/receive_block', methods=['POST'])
    def receive_block():
        blockchain = app.config["blockchain"]
        data = request.get_json()
        try:
            new_block = Block.from_dict(data)
            last_block = blockchain.get_last_block()
            blockchain.is_valid_block(new_block, last_block)
            blockchain.chain.append(new_block)
            return jsonify({"message": "Block added"}), 200
        except (InvalidPreviousHash, InvalidBlockHash, InvalidProofOfWork):
            # 👉 trigger resolusi sesuai spek
            sync_chain()
            return jsonify({"message": "Attempted sync due to conflict"}), 200
        except BlockchainError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/chain', methods=['GET'])
    def get_chain():
        blockchain = app.config["blockchain"]
        try:
            chain_data = [block.to_dict() for block in blockchain.chain]
            return jsonify(chain_data), 200
        except Exception as e:
            return jsonify({"error": f"Failed to serialize chain: {e}"}), 500

    @app.route('/register_node', methods=['POST'])
    def register_node():
        peers = app.config["peers"]
        try:
            node_address = request.get_json()['node']
            node_address = node_address.rstrip('/')
            if node_address not in peers:
                peers.add(node_address)
                response = {
                    "message": f"Node {node_address} added",
                    "peers": list(peers) + [request.host_url.rstrip('/')]
                }
                for peer in peers:
                    if peer != node_address:
                        try:
                            requests.post(f"{peer}/add_peer", json={"node": node_address})
                        except Exception as e:
                            print(f"⚠️ Broadcast peer gagal: {e}")
                return jsonify(response), 200
            else:
                return jsonify({"message": "Node already known"}), 200
        except KeyError:
            return jsonify({"error": "Missing node field"}), 400

    @app.route('/add_peer', methods=['POST'])
    def add_peer():
        peers = app.config["peers"]
        try:
            node_address = request.get_json()['node'].rstrip('/')
            if node_address not in peers:
                peers.add(node_address)
            return jsonify({"message": f"Peer {node_address} added"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to add peer: {e}"}), 400

    @app.route('/peers', methods=['GET'])
    def get_peers():
        peers = app.config["peers"]
        return jsonify(list(peers)), 200
    
    @app.route('/set_difficulty', methods=['POST'])
    def set_difficulty():
        blockchain = app.config["blockchain"]
        level = int(request.get_json()['difficulty'])
        blockchain.difficulty = max(1, level)
        return jsonify({"difficulty": blockchain.difficulty})

    def sync_chain():
        blockchain = app.config["blockchain"]
        peers = app.config["peers"]
        longest_chain = None
        max_length = len(blockchain.chain)
        for peer in peers:
            try:
                response = requests.get(f"{peer}/chain")
                chain_json = response.json()
                length = len(chain_json)
                chain = [Block.from_dict(b) for b in chain_json]
                if length > max_length and blockchain.is_valid_chain(chain):
                    max_length = length
                    longest_chain = chain
            except Exception as e:
                print(f"⚠️ Gagal sync dari {peer}: {e}")
                continue
        if longest_chain:
            print(f"🔄 Chain diganti. Panjang lama={len(blockchain.chain)}, baru={len(longest_chain)}")
            blockchain.replace_chain(longest_chain)
        else:
            print("✅ Tidak ada chain lebih panjang yang valid")
    app.sync_chain = sync_chain
    return app


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--difficulty", type=int, default=4)
    p.add_argument("--port", type=int, default=5001)
    args = p.parse_args()
    app = create_app(difficulty=args.difficulty)
    app.run(host="0.0.0.0", port=args.port)