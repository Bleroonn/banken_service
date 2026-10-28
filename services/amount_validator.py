from decimal import Decimal, InvalidOperation

from exceptions import ValidationError


class AmountValidator:

    def validate_amount(self, text):
        text = text.strip().replace(",", ".")
        try:
            amount = Decimal(text)
        except InvalidOperation:
            raise ValidationError("Bitte geben Sie einen gültigen Betrag ein.")

        if not amount.is_finite() or amount <= 0:
            raise ValidationError("Der Betrag muss grösser als 0 sein.")
        if amount.as_tuple().exponent < -2:
            raise ValidationError("Der Betrag darf höchstens zwei Nachkommastellen haben.")
        if amount > 1000000:
            raise ValidationError("Der Betrag darf höchstens CHF 1'000'000 sein.")
        return amount

    def validate_iban(self, text):
        iban = text.replace(" ", "").upper()
        if not iban.startswith("CH") or len(iban) != 21:
            raise ValidationError("Bitte geben Sie eine gültige IBAN ein.")
        return iban
