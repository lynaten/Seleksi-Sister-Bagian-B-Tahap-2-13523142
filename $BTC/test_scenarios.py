"""
Script untuk menjalankan beberapa skenario BTC sederhana.
Gunakan setelah menjalankan minimal 3 node (contoh: port 5001, 5002, 5003).
"""

import requests, time, json, hashlib

NODES = ["http://localhost:5001", "http://localhost:5002", "http://localhost:5003"]

def safe_get_json(url, method="get", **kwargs):
    """
    Wrapper aman untuk requests.get/post → selalu balikin (status_code, json_or_text).
    Tidak nge-raise error supaya kita bisa lihat payload error JSON dari server.
    """
    try:
        if method == "get":
            resp = requests.get(url, timeout=3, **kwargs)
        else:
            resp = requests.post(url, timeout=3, **kwargs)

        try:
            return resp.status_code, resp.json()
        except Exception:
            return resp.status_code, {"raw": resp.text}

    except Exception as e:
        return 0, {"error": str(e)}

def print_chain(node):
    code, data = safe_get_json(f"{node}/chain")
    if code != 200:
        print(f"❌ Gagal ambil chain dari {node}: {data}")
        return []

    chain = data
    print(f"⛓️ Chain di {node}: Panjang = {len(chain)}")
    for b in chain:
        print("   ", b['index'], b['hash'][:8], "Tx:", b['transactions'])
    return chain

# 1️⃣ Skenario transaksi + mining
def test_transaction_and_mining():
    print("\n=== Skenario 1: Transaksi & Mining ===")
    tx = {"sender": "Alice", "recipient": "Bob", "amount": 10}
    safe_get_json(f"{NODES[1]}/transaction", method="post", json=tx)

    code, mined = safe_get_json(f"{NODES[1]}/mine")
    if code == 200 and "hash" in mined:
        print("✅ Block hasil mining:", mined["hash"][:12], "Merkle:", mined.get("merkle_root"))
    else:
        print("❌ Mining gagal:", mined)

    time.sleep(1)
    for node in NODES:
        print_chain(node)

# 2️⃣ Skenario fork (2 node mining hampir bersamaan)
def test_fork_scenario():
    print("\n=== Skenario 2: Fork Longest Chain ===")
    safe_get_json(f"{NODES[1]}/transaction", method="post",
                  json={"sender": "Charlie", "recipient": "Diana", "amount": 5})
    safe_get_json(f"{NODES[2]}/transaction", method="post",
                  json={"sender": "Eve", "recipient": "Frank", "amount": 7})

    _, b2 = safe_get_json(f"{NODES[1]}/mine_local")
    _, b3 = safe_get_json(f"{NODES[2]}/mine_local")
    print("⛏️ Node2 mined:", b2.get("hash", "???")[:12])
    print("⛏️ Node3 mined:", b3.get("hash", "???")[:12])

    safe_get_json(f"{NODES[1]}/broadcast_block", method="post")
    safe_get_json(f"{NODES[2]}/broadcast_block", method="post")

    # safe_get_json(f"{NODES[2]}/transaction", method="post",
    #               json={"sender": "George", "recipient": "Helen", "amount": 12})
    # safe_get_json(f"{NODES[2]}/mine")

    time.sleep(2)
    for node in NODES:
        print_chain(node)

    # Node3 tambahin transaksi baru → bikin 1 block tambahan di atas fork B
    print("📥 Node3 menambah transaksi George→Helen lalu mining...")
    safe_get_json(f"{NODES[2]}/transaction", method="post",
                  json={"sender": "George", "recipient": "Helen", "amount": 12})
    _, b3_extra = safe_get_json(f"{NODES[2]}/mine")
    print("⛏️ Node3 mined extra block:", b3_extra.get("hash", "???")[:12])

    # Tunggu sinkronisasi
    time.sleep(2)
    for node in NODES:
        print_chain(node)
    print("✅ Hasil: Semua node harus ikut chain Node3 (yang lebih panjang)")

    # 🔥 Tambahan: Node1 coba mining lagi setelah chain sudah sinkron
    print("📥 Node1 coba menambah transaksi lama setelah kalah fork...")
    safe_get_json(f"{NODES[1]}/transaction", method="post",
                  json={"sender": "Charlie", "recipient": "Diana", "amount": 42})
    _, b1_extra = safe_get_json(f"{NODES[1]}/mine")
    print("⛏️ Node1 mined block baru:", b1_extra.get("hash", "???")[:12])

    time.sleep(2)
    for node in NODES:
        print_chain(node)
    print("✅ Hasil: Block Node1 juga ikut chain Node3 (bukan fork lama)")

# 3️⃣ Invalid block (Merkle Root rusak)
def test_invalid_merkle():
    print("\n=== Skenario 3: Invalid Merkle Root ===")
    _, chain = safe_get_json(f"{NODES[0]}/chain")
    if not chain or not isinstance(chain, list):
        print("❌ Gagal ambil chain awal:", chain)
        return

    last_block = chain[-1]
    tampered = last_block.copy()
    if isinstance(tampered["transactions"], list) and tampered["transactions"]:
        if isinstance(tampered["transactions"][0], dict):
            tampered["transactions"][0]["amount"] = 99999

    code, resp = safe_get_json(f"{NODES[0]}/receive_block", method="post", json=tampered)
    print("🚨 Kirim block rusak:", code, resp)
    time.sleep(2)
    for node in NODES:
        print_chain(node)

# 4️⃣ Invalid Proof-of-Work
def test_invalid_pow():
    print("\n=== Skenario 4: Invalid Proof-of-Work ===")
    _, chain = safe_get_json(f"{NODES[0]}/chain")
    if not chain or not isinstance(chain, list):
        print("❌ Gagal ambil chain awal:", chain)
        return

    last_block = chain[-1]
    fake_block = {
        "index": last_block["index"] + 1,
        "transactions": [{"sender": "Ivan", "recipient": "Jack", "amount": 99}],
        "timestamp": time.time(),
        "previous_hash": last_block["hash"],
        "nonce": 1,
    }

    block_string = json.dumps({
        "index": fake_block["index"],
        "transactions": fake_block["transactions"],
        "timestamp": fake_block["timestamp"],
        "previous_hash": fake_block["previous_hash"],
        "nonce": fake_block["nonce"],
        "merkle_root": hashlib.sha256(json.dumps(fake_block["transactions"]).encode()).hexdigest()
    }, sort_keys=True).encode()

    fake_block["hash"] = hashlib.sha256(block_string).hexdigest()

    code, resp = safe_get_json(f"{NODES[0]}/receive_block", method="post", json=fake_block)
    print("🚨 Kirim block PoW invalid:", code, resp)
    time.sleep(2)
    for node in NODES:
        print_chain(node)

if __name__ == "__main__":
    test_transaction_and_mining()
    test_fork_scenario()
    test_invalid_merkle()
    test_invalid_pow()