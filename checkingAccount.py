from transaction import Transaction

class CheckingAccount():
    """ Accounts with less interest and fewer transaction limits """
    def __init__(self, account_number: int) -> None:
        self._transactions = [Transaction]
        self._balance = 0
        self._account_number = account_number
    def _get_account_balance(self) -> int:
        """ Return account balance for current account """
        return self._balance
    def _get_account_number(self) -> int:
        """ Return account number for current account """
        return self._account_number

        