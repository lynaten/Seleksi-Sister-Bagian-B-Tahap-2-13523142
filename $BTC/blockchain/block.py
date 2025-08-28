import hashlib, json, time
from .exceptions import InvalidBlockHash

def calculate_merkle_root(transactions):
    """Hitung Merkle Root dari list transaksi"""
    if not transactions:
        return hashlib.sha256("".encode()).hexdigest()

    # kalau transaksi object/dict, ubah jadi string konsisten
    tx_hashes = [hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest() for tx in transactions]

    while len(tx_hashes) > 1:
        # kalau ganjil, duplikasi elemen terakhir
        if len(tx_hashes) % 2 != 0:
            tx_hashes.append(tx_hashes[-1])

        new_level = []
        for i in range(0, len(tx_hashes), 2):
            combined = tx_hashes[i] + tx_hashes[i+1]
            new_hash = hashlib.sha256(combined.encode()).hexdigest()
            new_level.append(new_hash)

        tx_hashes = new_level

    return tx_hashes[0]

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0, hash=None, merkle_root=None):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        # hitung merkle root kalau belum ada
        self.merkle_root = calculate_merkle_root(transactions)

        if hash:
            self.hash = hash
            if self.hash != self.calculate_hash():
                raise InvalidBlockHash(f"Invalid block hash at index {index}")
        else:
            self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "merkle_root": self.merkle_root
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def to_dict(self):
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "merkle_root": self.merkle_root,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            index=data["index"],
            transactions=data["transactions"],
            timestamp=data["timestamp"],
            previous_hash=data["previous_hash"],
            nonce=data["nonce"],
            hash=data.get("hash"),
            merkle_root=data.get("merkle_root")
        )
