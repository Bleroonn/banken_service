from decimal import Decimal
 
import pytest
 
from exceptions import ValidationError
from services.amount_validator import AmountValidator
 
validator = AmountValidator()
 
 
def test_gueltiger_betrag():
    assert validator.validate_amount("250.50") == Decimal("250.50")
    
def test_komma_wird_akzeptiert():
    assert validator.validate_amount("10,5") == Decimal("10.5")
 
 
@pytest.mark.parametrize("text", ["-50", "0", "abc", "10.555", "2000000", ""])
def test_ungueltige_betraege(text):
    with pytest.raises(ValidationError):
        validator.validate_amount(text)
 
 
def test_gueltige_iban():
    assert validator.validate_iban("ch32 0058 5585 1234 5601 t") == "CH320058558512345601T"
 
 
def test_ungueltige_iban():
    with pytest.raises(ValidationError):
        validator.validate_iban("CH123")