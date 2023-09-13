from transaction import Transaction
from decimal import Decimal
from datetime import datetime
class CheckingAccount():
    """ Accounts with less interest and fewer transaction limits """
    def __init__(self, account_number: int) -> None:
        self._transactions = [Transaction]
        self._balance = Decimal()
        self._account_number = account_number

    def _get_account_balance(self) -> int:
        """ Return account balance for current account """
        return self._balance
    
    def _get_account_number(self) -> int:
        """ Return account number for current account """
        return self._account_number
    
    def _register_transaction(self, amount:str, date:str) -> None:
        """ Update account's transactio history """
        new_transaction = Transaction()
        new_transaction._amount = amount
        new_transaction._date = date
        self._transactions.append(new_transaction)
        return 
    
    def _process_transaction(self, amount:str, date:str) -> None:
        """ Update account balance and transaction history """
        # Conditionaly update account balance
        print("CHECKING")
        if (Decimal(amount) < 0):
            prospective_balance = self._balance + Decimal(amount)
            if (prospective_balance >= 0):
                self._balance = prospective_balance
                self._register_transaction(amount, date)
            else:
                return
        else:
            self._balance += Decimal(amount)
            self._register_transaction(amount, date)

        return
    
    def _print_transactions(self) -> None:
        """ Display all recorded transactions for the acount """
        self._transactions.sort()
        for transaction in self._transactions:
            print(transaction)
        