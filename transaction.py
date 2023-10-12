from datetime import datetime
import decimal
from sqlalchemy.orm import declarative_base
from sqlalchemy import Integer, Column, ForeignKey, DateTime, DECIMAL, BOOLEAN
from database import Base

class Transaction(Base):
    # Create a "Transactions" table
    __tablename__ = "transaction"
    # Create table columns
    _id = Column(Integer, primary_key=True)
    _amount = Column(DECIMAL(precision=20, scale=10))
    _account_number = Column(Integer, ForeignKey("account._account_number"))
    _date = Column(DateTime)
    flag = Column(BOOLEAN)
    
    """ self._flag == True {Normal Transaction}; self._flag == False {Interest / Fees Transaction} """
    def __init__(self, date:datetime, amount:decimal.Decimal, flag:bool) -> None:
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
        self._amount = amount
        self._date = date
        self.flag = flag

    def transaction_amount(self) -> decimal.Decimal:
        """ Return transaction's value"""
        return self._amount
    
    def transaction_date(self) -> datetime:
        """ Return transaction's date and month """
        return self._date
    
    def __str__(self) -> str:
        return ("{0}, ${1}".format(self._date, f'{decimal.Decimal(self._amount):,.2f}'))

    def __lt__(self, other:datetime):
        return (self._date < other._date)
    
        