from decimal import Decimal
from datetime import datetime
from transaction import Transaction
from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, backref
from database import Base


class Account(Base):
     # Create a "Accounts" table
    __tablename__ = "account"

    # Create table columns
    _id = Column(Integer, primary_key=True)
    _bank_id = Column(Integer, ForeignKey("bank._id"))
    _account_number = Column(Integer)
    _balance = Column(DECIMAL(precision=20, scale=10))
    _transactions = relationship("Transaction", backref=backref("account"))
    _type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'account',
        'polymorphic_on':_type
    }
    def __init__(self, account_number:int) -> None:
        # self._transactions = []
        self._balance = Decimal()
        self._account_number = account_number

    def get_account_balance(self) -> int:
        """ Return account balance for current account """
        return self._balance

    def get_account_number(self) -> int:
        """ Return account number for current account """
        return self._account_number
    
    def print_transactions(self) -> None:
        """ Display all recorded transactions for the acount """
        self._transactions.sort()
        for transaction in self._transactions:
            print(transaction.__str__()[0])
    def list_transactions(self) -> list:
        """ Return a list of transaction tuples for given account -> [(transaction summary, transaction_value_flag)] """
        return [transaction.__str__() for transaction in self._transactions]

    def register_transaction(self, amount:Decimal, date:datetime, flag:bool, session) -> None:
        """ Update account's transactio history """
        new_transaction = Transaction(date, amount, flag)
        self._transactions.append(new_transaction)
        session.add(new_transaction)
        return 

    def check_transaction_date(self, date: datetime) -> (bool, datetime):
        """ Ensures transaction is chronologically correct """
        if (len(self._transactions) > 0):
            most_recent_transaction_date = max([i.transaction_date() for i in self._transactions])
            most_recent_transaction_date = most_recent_transaction_date.date()
            if(date < most_recent_transaction_date):
                return (False, most_recent_transaction_date)
            else:
                return (True, most_recent_transaction_date)
        else:
            return (True, date)
        
    def check_interest_fees(self, date:datetime) -> bool:
        """ Ensures interest and fees have not applied before"""
        interest_fees_transactions = [transaction for transaction in self._transactions if ((transaction.transaction_date().month == date.month) and (not transaction.flag))]
        if (len(interest_fees_transactions) > 0):
            return False
        else:
            return True 