from exceptions import AccountNotFoundError, BankError, InsufficientFundsError, ValidationError
from models import Transaction


class BankService:

    def __init__(self, db, repository, validator):
        self.db = db
        self.repository = repository
        self.validator = validator

    def get_all_customers(self):
        return self.repository.find_all_customers()

    def get_accounts(self, customer_id):
        return self.repository.find_accounts(customer_id)

    def get_account(self, account_id):
        account = self.repository.find_account_by_id(account_id)
        if account is None:
            raise AccountNotFoundError("Das Konto wurde nicht gefunden.")
        return account

    def get_latest_transactions(self, account_id):
        return self.repository.find_latest_transactions(account_id)

    def deposit(self, account_id, amount_text):
        try:
            amount = self.validator.validate_amount(amount_text)
            account = self.load_account_for_booking(account_id)

            account.balance += amount
            self.repository.update_balance(account.id, account.balance)
            self.repository.add_transaction(Transaction(account.id, "C", "Einzahlung", amount))

            self.db.commit()
            return account
        except BankError:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise BankError("Die Einzahlung konnte wegen eines technischen Problems nicht ausgeführt werden. Es wurde nichts gebucht.")

    def withdraw(self, account_id, amount_text):
        try:
            amount = self.validator.validate_amount(amount_text)
            account = self.load_account_for_booking(account_id)

            if amount > account.available_amount():
                raise InsufficientFundsError(
                    f"Der Betrag übersteigt den verfügbaren Betrag von CHF {account.available_amount()}. Es wurde nichts gebucht."
                )

            account.balance -= amount
            self.repository.update_balance(account.id, account.balance)
            self.repository.add_transaction(Transaction(account.id, "D", "Auszahlung", amount))

            self.db.commit()
            return account
        except BankError:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise BankError("Die Abhebung konnte wegen eines technischen Problems nicht ausgeführt werden. Es wurde nichts gebucht.")

    def transfer(self, account_id, iban_text, amount_text):
        try:
            amount = self.validator.validate_amount(amount_text)
            iban = self.validator.validate_iban(iban_text)

            source = self.load_account_for_booking(account_id)
            if source.iban == iban:
                raise ValidationError("Eine Überweisung auf das gleiche Konto ist nicht möglich.")

            target = self.repository.find_account_by_iban(iban, lock=True)
            if target is None:
                raise AccountNotFoundError("Die IBAN existiert nicht. Bitte prüfen Sie die Eingabe. Es wurde nichts gebucht.")

            if amount > source.available_amount():
                raise InsufficientFundsError(
                    f"Der Betrag übersteigt den verfügbaren Betrag von CHF {source.available_amount()}. Es wurde nichts gebucht."
                )

            source.balance -= amount
            target.balance += amount
            
            self.repository.update_balance(source.id, source.balance)
            self.repository.update_balance(target.id, target.balance)
            self.repository.add_transaction(Transaction(source.id, "D", f"An {target.iban}", amount))
            self.repository.add_transaction(Transaction(target.id, "C", f"Von {source.iban}", amount))

            self.db.commit()
            return source
        except BankError:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise BankError("Die Überweisung konnte wegen eines technischen Problems nicht ausgeführt werden. Es wurde nichts gebucht.")

    def load_account_for_booking(self, account_id):
        account = self.repository.find_account_by_id(account_id, lock=True)
        if account is None:
            raise AccountNotFoundError("Das Konto wurde nicht gefunden.")
        return account
