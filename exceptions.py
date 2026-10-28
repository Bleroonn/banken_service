class BankError(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ValidationError(BankError):
    pass


class InsufficientFundsError(BankError):
    pass


class AccountNotFoundError(BankError):
    pass
