import time
from .block import Block, calculate_merkle_root
from .exceptions import InvalidPreviousHash, InvalidBlockHash, InvalidProofOfWork, InvalidChain, BlockchainError
class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.transaction_pool = []

    def create_genesis_block(self):
        return Block(0, ["Genesis Block"], 0, "0")

    def get_last_block(self):
        return self.chain[-1]

    def add_transaction(self, tx):
        self.transaction_pool.append(tx)

    def proof_of_work(self, block):
        while not block.hash.startswith("0" * self.difficulty):
            block.nonce += 1
            block.hash = block.calculate_hash()
        return block.hash

    def mine_block(self):
        if not self.transaction_pool:
            return None
        new_block = Block(
            len(self.chain),
            [tx for tx in self.transaction_pool],
            time.time(),
            self.get_last_block().hash
        )
        self.proof_of_work(new_block)
        self.chain.append(new_block)
        self.transaction_pool = []
        return new_block
    
    def is_valid_block(self, block, prev_block):
        if block.index != prev_block.index + 1:
            raise InvalidBlockHash(f"Block {block.index}: wrong index")
        if block.previous_hash != prev_block.hash:
            raise InvalidPreviousHash(...)
        # verifikasi merkle root berasal dari transaksi
        if block.merkle_root != calculate_merkle_root(block.transactions):
            raise InvalidBlockHash(f"Block {block.index}: merkle root mismatch")
        if block.hash != block.calculate_hash():
            raise InvalidBlockHash(...)
        if not block.hash.startswith("0" * self.difficulty):
            raise InvalidProofOfWork(...)
        return True

    def is_valid_chain(self, chain):
        for i in range(1, len(chain)):
            try:
                self.is_valid_block(chain[i], chain[i-1])
            except BlockchainError as e:
                raise InvalidChain(f"Chain invalid at index {i}: {str(e)}")
        return True

    def replace_chain(self, new_chain):
        if len(new_chain) > len(self.chain) and self.is_valid_chain(new_chain):
            print("Replacing local chain with longer valid chain")
            self.chain = new_chain
            return True
        print("ℹChain not replaced (shorter or invalid)")
        return False