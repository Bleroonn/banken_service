from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Customer:
    id: int
    customer_number: str
    first_name: str
    last_name: str


@dataclass
class Account:
    id: int
    iban: str
    balance: Decimal
    overdraft: Decimal
    customer_id: int

    def available_amount(self):
        return self.balance + self.overdraft


@dataclass
class Transaction:
    account_id: int
    type: str
    text: str
    amount: Decimal
