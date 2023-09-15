from decimal import Decimal
from transaction import Transaction

class Account():
    def __init__(self, account_number:int) -> None:
        self._transactions = []
        self._balance = Decimal()
        self._account_number = account_number

    def _get_account_balance(self) -> int:
        """ Return account balance for current account """
        return self._balance

    def _get_account_number(self) -> int:
        """ Return account number for current account """
        return self._account_number
    
    def _print_transactions(self) -> None:
        """ Display all recorded transactions for the acount """
        self._transactions.sort()
        for transaction in self._transactions:
            print(transaction)
    
