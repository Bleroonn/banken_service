from flask import Blueprint, render_template, request

from database import Database
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
