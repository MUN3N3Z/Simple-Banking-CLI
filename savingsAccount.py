from transaction import Transaction
import decimal
from datetime import datetime, timedelta
from collections import defaultdict
from account import Account
from utils import OverdrawError, TransactionSequenceError, TransactionLimitError

class SavingsAccount(Account):
    """Accounts with more interest and more transactions limits"""
    def __init__(self, account_number) -> None:
        super().__init__(account_number)
        self._transaction_dates = defaultdict(int)
        self._transaction_months = defaultdict(int)
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
        self._transaction_dates[date] += 1
        self._transaction_months[date.month] += 1
        return 
    
    def _process_transaction(self, amount:decimal.Decimal, date:datetime) -> None:
        """ Update account balance and transaction history """
            # Ensure daily and monthly transaction limits are not exceeded
        if (self._transaction_dates[date] == 2):
            raise TransactionLimitError(True)
        elif (self._transaction_months[date.month] == 5):
            raise(TransactionLimitError(False))
        else:
            # Conditionaly update account balance
            if (self.check_transaction_date(date=date)[0]):
                if (decimal.Decimal(amount) < 0):
                    prospective_balance = self._balance + amount
                    if (prospective_balance >= 0):
                        self._balance = prospective_balance
                        self._register_transaction(amount, date, True)
                    else:
                        # Raise OverDraw error if transaction will overdraw the account
                        raise OverdrawError
                else:
                    self._balance += amount
                    self._register_transaction(amount, date, True)
            else:
                raise TransactionSequenceError(self.check_transaction_date(date=date)[1], True)

    def _compute_interest_fees(self):
        """ Compute and apply interest for savings account """
        if (len(self._transactions) > 0):
            most_recent_transaction_date = max(self._transaction_dates.keys())
            # Ensure monthly interest hasn't been applied
            if (self.check_interest_fees(most_recent_transaction_date)):
                interest = decimal.Decimal(0.0041) * self._balance
                # Find date to apply interest
                first_day_of_next_month = datetime(most_recent_transaction_date.year, most_recent_transaction_date.month + 1, 1)
                last_day_of_month = first_day_of_next_month - timedelta(days=1)
                # Register transaction
                self._register_transaction(interest, last_day_of_month.date(), False)
                # Update account balance
                self._balance += interest
            else:
                raise TransactionSequenceError(most_recent_transaction_date, False)
        return