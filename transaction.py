from datetime import datetime
import decimal
class Transaction():
    """ self._flag == True {Normal Transaction}; self._flag == False {Interest / Fees Transaction} """
    def __init__(self, flag:bool) -> None:
        self._amount = None
        self._date = None
        self.flag = flag
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP

    def _transaction_amount(self) -> decimal.Decimal:
        """ Return transaction's value"""
        return self._amount
    
    def _transaction_date(self) -> datetime:
        """ Return transaction's date and month """
        return self._date
    
    def __str__(self) -> str:
        return ("{0}, ${1}".format(self._date, f'{decimal.Decimal(self._amount):,.2f}'))

    def __lt__(self, other:datetime):
        return (self._date < other._date)
    
        