from models import Customer, Account


class BankRepository:

    def __init__(self, db):
        self.db = db

    def find_all_customers(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM CUSTOMER ORDER BY LAST_NAME")
        rows = cursor.fetchall()
        cursor.close()
        return [Customer(r["ID"], r["CUSTOMER_NUMBER"], r["FIRST_NAME"], r["LAST_NAME"]) for r in rows]

    def find_accounts(self, customer_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM ACCOUNT WHERE CUSTOMER_ID = %s", (customer_id,))
        rows = cursor.fetchall()
        cursor.close()
        return [self.to_account(r) for r in rows]

    def find_account_by_id(self, account_id, lock=False):
        sql = "SELECT * FROM ACCOUNT WHERE ID = %s"
        if lock:
            # beim booking muss das konto gelockt werden damit nicht doppelt transaaktionen passieren
            sql += " FOR UPDATE"
        cursor = self.db.cursor()
        cursor.execute(sql, (account_id,))
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return None
        return self.to_account(row)

    def find_account_by_iban(self, iban, lock=False):
        sql = "SELECT * FROM ACCOUNT WHERE IBAN = %s"
        if lock:
            sql += " FOR UPDATE"
        cursor = self.db.cursor()
        cursor.execute(sql, (iban,))
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return None
        return self.to_account(row)

    def update_balance(self, account_id, balance):
        cursor = self.db.cursor()
        cursor.execute("UPDATE ACCOUNT SET BALANCE = %s WHERE ID = %s", (balance, account_id))
        cursor.close()

    def add_transaction(self, transaction):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO TRANSACTION_RECORD (TYPE, TEXT, AMOUNT, TRANSACTION_TIME, ACCOUNT_ID) "
            "VALUES (%s, %s, %s, NOW(), %s)",
            (transaction.type, transaction.text, transaction.amount, transaction.account_id),
        )
        cursor.close()

    def find_latest_transactions(self, account_id):
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM TRANSACTION_RECORD WHERE ACCOUNT_ID = %s "
            "ORDER BY TRANSACTION_TIME DESC LIMIT 10",
            (account_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def to_account(self, row):
        return Account(row["ID"], row["IBAN"], row["BALANCE"], row["OVERDRAFT"], row["CUSTOMER_ID"])
