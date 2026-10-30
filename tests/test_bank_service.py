from decimal import Decimal
 
import pytest
 
from exceptions import AccountNotFoundError, BankError, InsufficientFundsError, ValidationError
from models import Account
from services.amount_validator import AmountValidator
from services.bank_service import BankService
 
KONTO_A = "CH320058558512345601T"
KONTO_B = "CH320058558512345601M"
 
 
class FakeRepository:
 
    def __init__(self):
        self.ibans = {1: KONTO_A, 2: KONTO_B}
        self.balances = {1: Decimal("900.00"), 2: Decimal("0.00")}
        self.overdrafts = {1: Decimal("1000.00"), 2: Decimal("0.00")}
        self.transactions = []
        self.pending_balances = {}
        self.pending_transactions = []
        self.fail = False
 
    def find_account_by_id(self, account_id, lock=False):
        if account_id not in self.ibans:
            return None
        return Account(account_id, self.ibans[account_id], self.balances[account_id], self.overdrafts[account_id], 1)
 
    def find_account_by_iban(self, iban, lock=False):
        for account_id, value in self.ibans.items():
            if value == iban:
                return self.find_account_by_id(account_id)
        return None
 
    def update_balance(self, account_id, balance):
        self.pending_balances[account_id] = balance
 
    def add_transaction(self, transaction):
        if self.fail:
            raise RuntimeError("Datenbank nicht erreichbar")
        self.pending_transactions.append(transaction)
 
 
class FakeDatabase:
 
    def __init__(self, repository):
        self.repository = repository
 
    def commit(self):
        self.repository.balances.update(self.repository.pending_balances)
        self.repository.transactions += self.repository.pending_transactions
        self.rollback()
 
    def rollback(self):
        self.repository.pending_balances = {}
        self.repository.pending_transactions = []
 
 
@pytest.fixture
def repository():
    return FakeRepository()
 
 
@pytest.fixture
def service(repository):
    return BankService(FakeDatabase(repository), repository, AmountValidator())
 
 
def test_einzahlen(service, repository):
    account = service.deposit(1, "250")
    assert account.balance == Decimal("1150.00")
    assert repository.balances[1] == Decimal("1150.00")
    assert repository.transactions[0].type == "C"
 
 
def test_einzahlen_ungueltiger_betrag(service, repository):
    with pytest.raises(ValidationError):
        service.deposit(1, "-50")
    assert repository.balances[1] == Decimal("900.00")
    assert repository.transactions == []
 
 
def test_einzahlen_unbekanntes_konto(service):
    with pytest.raises(AccountNotFoundError):
        service.deposit(99, "100")
 
 
def test_abheben(service, repository):
    service.withdraw(1, "500")
    assert repository.balances[1] == Decimal("400.00")
    assert repository.transactions[0].type == "D"
 
 
def test_abheben_bis_zum_limit(service, repository):
    service.withdraw(1, "1900")
    assert repository.balances[1] == Decimal("-1000.00")
 
 
def test_abheben_ueber_limit(service, repository):
    with pytest.raises(InsufficientFundsError):
        service.withdraw(1, "1900.01")
    assert repository.balances[1] == Decimal("900.00")
 
 
def test_ueberweisen(service, repository):
    service.transfer(1, KONTO_B, "100")
    assert repository.balances[1] == Decimal("800.00")
    assert repository.balances[2] == Decimal("100.00")
    assert [t.type for t in repository.transactions] == ["D", "C"]
 
 
def test_ueberweisen_unbekannte_iban(service, repository):
    with pytest.raises(AccountNotFoundError):
        service.transfer(1, "CH0000000000000000000", "100")
    assert repository.balances[1] == Decimal("900.00")
 
 
def test_ueberweisen_ueber_limit(service, repository):
    with pytest.raises(InsufficientFundsError):
        service.transfer(2, KONTO_A, "50")
    assert repository.balances[2] == Decimal("0.00")
 
 
def test_ueberweisen_auf_eigenes_konto(service):
    with pytest.raises(ValidationError):
        service.transfer(1, KONTO_A, "100")
 
 
def test_rollback_bei_datenbankfehler(service, repository):
    repository.fail = True
    with pytest.raises(BankError):
        service.transfer(1, KONTO_B, "100")
    assert repository.balances[1] == Decimal("900.00")
    assert repository.balances[2] == Decimal("0.00")
    assert repository.transactions == []