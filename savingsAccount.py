from transaction import Transaction

class SavingsAccount():
    """Accounts with more interest and more transactions limits"""
    def __init__(self, account_number) -> None:
        self._transactions = [Transaction]
        self._balance = 0
        self._account_number = account_number
    def _get_account_balance(self) -> int:
        """ Return account balance for current account """
        return self._balance
    def _get_account_number(self) -> int:
        """ Return account number for current account """
        return self._account_number