from .exceptions import TransactionError

class Transaction:
    def __init__(self, sender, recipient, amount):
        if not sender or not recipient:
            raise TransactionError("Transaction must have sender and recipient")
        if amount <= 0:
            raise TransactionError("Transaction amount must be > 0")

        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def to_dict(self):
        return {"sender": self.sender, "recipient": self.recipient, "amount": self.amount}
