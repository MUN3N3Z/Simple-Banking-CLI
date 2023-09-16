from datetime import datetime
import decimal
class Transaction():
    def __init__(self) -> None:
        self._amount = None
        self._date = None
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP


    def _transaction_amount(self) -> str:
        """ Return transaction's value"""
        return self._amount
    
    def _transaction_date(self) -> (str, int):
        """ Return transaction's date and month """
        date_object = datetime.strptime(self._date, "%Y-%m-%d")
        return (self._date, date_object.month)
    
    def __str__(self) -> str:
        return ("{0}, ${1}".format(self._date, f'{decimal.Decimal(self._amount):,.2f}'))

    def __lt__(self, other):
        return (datetime.strptime(self._date, "%Y-%m-%d") < datetime.strptime(other._date, "%Y-%m-%d"))
    
        