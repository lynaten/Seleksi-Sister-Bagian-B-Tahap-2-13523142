# exceptions.py
class BlockchainError(Exception):
    """Base class for blockchain errors."""

class InvalidBlockHash(BlockchainError):
    pass

class InvalidPreviousHash(BlockchainError):
    pass

class InvalidProofOfWork(BlockchainError):
    pass

class InvalidChain(BlockchainError):
    pass

class TransactionError(BlockchainError):
    pass
