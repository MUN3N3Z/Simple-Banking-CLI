from transaction import Transaction
import decimal
from datetime import datetime, timedelta
from account import Account
from utils import OverdrawError, TransactionSequenceError

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
    
    def _register_transaction(self, amount:decimal.Decimal, date:datetime, flag:bool) -> None:
        """ Update account's transactio history """
        new_transaction = Transaction(flag=flag)
        new_transaction._amount = amount
        new_transaction._date = date
        self._transactions.append(new_transaction)
        return 
    
    def _process_transaction(self, amount:decimal.Decimal, date:datetime) -> None:
        """ Update account balance and transaction history """
        # Conditionaly update account balance
        if (self.check_transaction_date(date=date)[0]):
            # Check chronology of transaction dates
            if (decimal.Decimal(amount) < 0):
                # Avoid overdrawing the account
                prospective_balance = self._balance + decimal.Decimal(amount)
                if (prospective_balance >= 0):
                    self._balance = prospective_balance
                    self._register_transaction(amount, date, True)
                else:
                    raise OverdrawError
            else:
                self._balance += amount
                self._register_transaction(amount, date, True)
        else:
            raise TransactionSequenceError(self.check_transaction_date(date=date)[1])
        

    def _compute_interest_fees(self):
        """ Compute and apply interest and fees for checking account """
        if (len(self._transactions) > 0):
            transaction_dates = (transaction._transaction_date() for transaction in self._transactions)
            most_recent_transaction_date = max(transaction_dates)
            if (self.check_interest_fees(most_recent_transaction_date)):
                # Find date to apply interest
                last_day_of_month = datetime(most_recent_transaction_date.year, most_recent_transaction_date.month + 1, 1) - timedelta(days=1)
                # Compute and register interest
                interest_fees = decimal.Decimal(0.0008) * self._balance
                self._register_transaction((interest_fees), last_day_of_month.date(), False)
                # Conditionally apply fees
                if (self._balance < 100):
                    self._register_transaction(decimal.Decimal(-5.44), last_day_of_month.date(), False)
                    self._balance -= decimal.Decimal(5.44)
                # Update account balance
                self._balance += interest_fees
            else:
                raise TransactionSequenceError(most_recent_transaction_date, False)
        return
        
        