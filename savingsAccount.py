from transaction import Transaction
import decimal
from datetime import datetime, timedelta
from collections import defaultdict
from account import Account
from utils import OverdrawError, TransactionSequenceError, TransactionLimitError
from sqlalchemy import Integer, Column, ForeignKey
from collections import Counter

class SavingsAccount(Account):
    """Accounts with more interest and more transactions limits"""
    # Create a "savings_account" table
    __tablename__ = "savings_account"
    # Create table columns
    _id = Column(Integer, ForeignKey("account._id"), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity':'savings_account',
    }

    def __init__(self, account_number) -> None:
        super().__init__(account_number)
        # self._transaction_dates = defaultdict(int)
        # self._transaction_months = defaultdict(int)
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP

    @property
    def balance(self):
        return super().get_account_balance()
    
    @property
    def account_number(self):
        return super().get_account_number()
    def _check_date_limit(self, date, transactions: list[Transaction]):
        # Count number of transactions on "date"
        number_of_transactions = 0
        for transaction in transactions:
            if (transaction.transaction_date().date() == date):
                number_of_transactions += 1
        print(number_of_transactions)
        return (number_of_transactions < 2)
        
    def _check_month_limit(self, date, transactions:list[Transaction]):
        # Count number of transactions on "date".month
        number_of_transactions = 0
        for i in transactions:
            if (i.transaction_date().month == date.month and i.transaction_date().year == date.year):
                number_of_transactions += 1
        print(number_of_transactions)
        return (number_of_transactions < 5)
    
    def process_transaction(self, amount:decimal.Decimal, date, session) -> None:
        """ Update account balance and transaction history """
        # Filter out interest & fees transactions for "_check_month_limit and _check_date_limit" functions
        valid_transactions = list(filter(lambda x: x.flag == True, self._transactions))
        # Ensure daily and monthly transaction limits are not exceeded
        if (not self._check_date_limit(date, valid_transactions)):
            raise TransactionLimitError(True)
        elif (not self._check_month_limit(date, valid_transactions)):
            raise(TransactionLimitError(False))
        else:
            # Conditionaly update account balance
            if (self.check_transaction_date(date=date)[0]): # Ensure transactions are chronological
                if (decimal.Decimal(amount) < 0):
                    prospective_balance = self._balance + amount
                    if (prospective_balance >= 0):
                        self._balance = prospective_balance
                        self.register_transaction(amount, date, True, session)
                    else:
                        # Raise OverDraw error if transaction will overdraw the account
                        raise OverdrawError
                else:
                    self._balance += amount
                    self.register_transaction(amount, date, True, session)
            else:
                raise TransactionSequenceError(self.check_transaction_date(date=date)[1], True)

    def compute_interest_fees(self, session):
        """ Compute and apply interest for savings account """
        if (len(self._transactions) > 0):
            most_recent_transaction_date = max([transaction.transaction_date() for transaction in self._transactions])
            # Ensure monthly interest hasn't been applied
            if (self.check_interest_fees(most_recent_transaction_date)):
                interest = decimal.Decimal(0.0041) * self._balance
                # Find date to apply interest
                first_day_of_next_month = datetime(most_recent_transaction_date.year, most_recent_transaction_date.month + 1, 1)
                last_day_of_month = first_day_of_next_month - timedelta(days=1)
                # Register transaction
                self.register_transaction(interest, last_day_of_month.date(), False, session)
                # Update account balance
                self._balance += interest
            else:
                raise TransactionSequenceError(most_recent_transaction_date, False)
        return