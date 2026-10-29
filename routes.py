from flask import Blueprint, abort, render_template, request

from database import Database
from exceptions import AccountNotFoundError, BankError
from repositories.bank_repository import BankRepository
from services.amount_validator import AmountValidator
from services.bank_service import BankService

bp = Blueprint("bank", __name__)


def create_service():
    db = Database()
    return db, BankService(db, BankRepository(db), AmountValidator())


@bp.route("/")
def select_account():
    db, service = create_service()
    try:
        customers = service.get_all_customers()
        customer_id = request.args.get("customer_id", type=int)
        accounts = service.get_accounts(customer_id) if customer_id else []
    finally:
        db.close()
    return render_template("konto_waehlen.html", customers=customers, accounts=accounts, customer_id=customer_id)


@bp.route("/konto/<int:account_id>")
def show_overview(account_id):
    db, service = create_service()
    try:
        account = service.get_account(account_id)
        transactions = service.get_latest_transactions(account_id)
    except AccountNotFoundError:
        abort(404)
    finally:
        db.close()
    return render_template("uebersicht.html", account=account, transactions=transactions)


@bp.route("/konto/<int:account_id>/einzahlen", methods=["GET", "POST"])
def deposit(account_id):
    db, service = create_service()
    message = None
    error = None
    try:
        if request.method == "POST":
            try:
                account = service.deposit(account_id, request.form["amount"])
                message = f"Einzahlung erfolgreich. Neuer Kontostand: CHF {account.balance}"
            except BankError as e:
                error = e.message
        account = service.get_account(account_id)
    except AccountNotFoundError:
        abort(404)
    finally:
        db.close()
    return render_template("einzahlen.html", account=account, message=message, error=error)


@bp.route("/konto/<int:account_id>/abheben", methods=["GET", "POST"])
def withdraw(account_id):
    db, service = create_service()
    message = None
    error = None
    try:
        if request.method == "POST":
            try:
                account = service.withdraw(account_id, request.form["amount"])
                message = f"Abhebung erfolgreich. Neuer Kontostand: CHF {account.balance}"
            except BankError as e:
                error = e.message
        account = service.get_account(account_id)
    except AccountNotFoundError:
        abort(404)
    finally:
        db.close()
    return render_template("abheben.html", account=account, message=message, error=error)


@bp.route("/konto/<int:account_id>/ueberweisen", methods=["GET", "POST"])
def transfer(account_id):
    db, service = create_service()
    message = None
    error = None
    try:
        if request.method == "POST":
            try:
                account = service.transfer(account_id, request.form["iban"], request.form["amount"])
                message = f"Überweisung erfolgreich. Neuer Kontostand: CHF {account.balance}"
            except BankError as e:
                error = e.message
        account = service.get_account(account_id)
    except AccountNotFoundError:
        abort(404)
    finally:
        db.close()
    return render_template("ueberweisen.html", account=account, message=message, error=error)
