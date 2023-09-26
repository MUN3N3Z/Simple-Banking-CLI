from decimal import Decimal
from datetime import datetime
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

    def check_transaction_date(self, date: datetime) -> (bool, datetime):
        """ Ensures transaction is chronologically correct """
        if (len(self._transactions) > 0):
            most_recent_transaction_date = max([i._transaction_date() for i in self._transactions])
            if(date < most_recent_transaction_date):
                return (False, most_recent_transaction_date)
            else:
                return (True, most_recent_transaction_date)
        else:
            return (True, date)
        
    def check_interest_fees(self, date:datetime) -> bool:
        """ Ensures interest and fees have not applied before"""
        interest_fees_transactions = [transaction for transaction in self._transactions if ((transaction._transaction_date().month == date.month) and (not transaction.flag))]
        if (len(interest_fees_transactions) > 0):
            return False
        else:
            return True 