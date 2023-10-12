from transaction import Transaction
import decimal, logging
from datetime import datetime, timedelta
from account import Account
from utils import OverdrawError, TransactionSequenceError
from sqlalchemy import Integer, Column, ForeignKey

class CheckingAccount(Account):
    """ Accounts with less interest and fewer transaction limits """
    # Create a "checking_account" table
    __tablename__ = "checking_account"
    # Create table columns
    _id = Column(Integer, ForeignKey("account._id"), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity':'checking_account',
    }

    def __init__(self, account_number: int) -> None:
        super().__init__(account_number)
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP

    @property
    def balance(self):
        return super().get_account_balance()
    
    @property
    def account_number(self):
        return super().get_account_number()
    
    def process_transaction(self, amount:decimal.Decimal, date, session) -> None:
        """ Update account balance and transaction history """
        # Conditionaly update account balance
        if (self.check_transaction_date(date=date)[0]): # Ensure transactions are chronological
            # Check chronology of transaction dates
            if (decimal.Decimal(amount) < 0):
                # Avoid overdrawing the account
                prospective_balance = self._balance + decimal.Decimal(amount)
                if (prospective_balance >= 0):
                    self._balance = prospective_balance
                    self.register_transaction(amount, date, True, session)
                else:
                    raise OverdrawError
            else:
                self._balance += amount
                self.register_transaction(amount, date, True, session)
        else:
            raise TransactionSequenceError(self.check_transaction_date(date=date)[1], True)
        

    def compute_interest_fees(self, session):
        """ Compute and apply interest and fees for checking account """
        if (len(self._transactions) > 0):
            transaction_dates = (transaction.transaction_date() for transaction in self._transactions)
            most_recent_transaction_date = max(transaction_dates)
            if (self.check_interest_fees(most_recent_transaction_date)):
                # Find date to apply interest
                last_day_of_month = datetime(most_recent_transaction_date.year, most_recent_transaction_date.month + 1, 1) - timedelta(days=1)
                # Compute and register interest
                interest_fees = decimal.Decimal(0.0008) * self._balance
                self.register_transaction((interest_fees), last_day_of_month.date(), False, session)
                # Conditionally apply fees
                if (self._balance < 100):
                    self.register_transaction(decimal.Decimal(-5.44), last_day_of_month.date(), False, session)
                    self._balance -= decimal.Decimal(5.44)
                    # Log fees
                    logging.debug(f'Created transaction: {self.account_number}, -5.44')
                # Update account balance
                self._balance += interest_fees
            else:
                raise TransactionSequenceError(most_recent_transaction_date, False)
        return
        
        