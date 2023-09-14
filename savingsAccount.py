from transaction import Transaction
from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict

class SavingsAccount():
    """Accounts with more interest and more transactions limits"""
    def __init__(self, account_number) -> None:
        self._transactions = []
        self._balance = Decimal()
        self._account_number = account_number
        self._transaction_dates = defaultdict(int)
        self._transaction_months = defaultdict(int)

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
        self._transaction_dates[date] += 1
        self._transaction_months[datetime.strptime(date, "%Y-%m-%d").month] += 1
        return 
    
    def _process_transaction(self, amount:str, date:str) -> None:
        """ Update account balance and transaction history """
            # Ensure daily and monthly transaction limits are not exceeded
        if (self._transaction_dates[date] == 2 or self._transaction_months[datetime.strptime(date, "%Y-%m-%d").month] == 5):
            return
        else:
            # Conditionaly update account balance
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

    def _compute_interest_fees(self):
        """ Compute and apply interest for savings account """
        interest = Decimal(0.0041) * self._balance
        # Find most recent transaction date
        transaction_dates = self._transaction_dates.keys()
        most_recent_transaction_date = max([datetime.strptime(transaction_date, "%Y-%m-%d") for transaction_date in transaction_dates])
        first_day_of_next_month = datetime(most_recent_transaction_date.year, most_recent_transaction_date.month + 1, 1)
        last_day_of_month = first_day_of_next_month - timedelta(days=1)
        # Register transaction
        self._register_transaction(str(interest), str(last_day_of_month.date()))
        # Update account balance
        self._balance += interest
        return