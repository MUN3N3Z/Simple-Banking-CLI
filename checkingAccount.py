from transaction import Transaction
import decimal
from datetime import datetime, timedelta
from account import Account

class CheckingAccount(Account):
    """ Accounts with less interest and fewer transaction limits """
    def __init__(self, account_number: int) -> None:
        super().__init__(account_number)
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP


    @property
    def balance(self):
        return super()._get_account_balance()
    
    @property
    def account_number(self):
        return super()._get_account_number()
    
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
        if (decimal.Decimal(amount) < 0):
            prospective_balance = self._balance + decimal.Decimal(amount)
            if (prospective_balance >= 0):
                self._balance = prospective_balance
                self._register_transaction(amount, date)
            else:
                return
        else:
            self._balance += decimal.Decimal(amount)
            self._register_transaction(amount, date)

        return

    def _compute_interest_fees(self):
        """ Compute and apply interest and fees for checking account """
        # Find most recent transaction date
        transaction_dates = (transaction._transaction_date()[0] for transaction in self._transactions)
        most_recent_transaction_date = max([datetime.strptime(transaction_date, "%Y-%m-%d") for transaction_date in transaction_dates])
        last_day_of_next_month = datetime(most_recent_transaction_date.year, most_recent_transaction_date.month + 1, 1) - timedelta(days=1)
        # Compute and register interest
        interest_fees = decimal.Decimal(0.0008) * self._balance
        self._register_transaction(str(interest_fees), str(last_day_of_next_month.date()))
        # Conditionally apply fees
        if (self._balance < 100):
            self._register_transaction("-5.44", str(last_day_of_next_month.date()))
            self._balance -= decimal.Decimal(5.44)
        
        # Update account balance
        self._balance += interest_fees

        return
        
        