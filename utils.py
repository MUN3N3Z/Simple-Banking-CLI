from datetime import datetime
import logging
class OverdrawError(ValueError):
    """ When a negative transaction will exceed the account balance """
    def __init__(self) -> None:
        self._message = "This transaction could not be completed due to an insufficient account balance."
        super().__init__(self._message)
    def __str__(self) -> str:
        return super().__str__()
    def __repr__(self) -> str:
        return f'OverdrawError: {self._message}'

class TransactionSequenceError(ValueError):
    """ When a transaction does not follow the chronological order """
    def __init__(self, date:datetime, flag: bool) -> None:
        # Flag values: True - wrong transaction sequence; False - Interest and fees already applied
        month = date.strftime("%B")
        if (flag):
            self._message = f'New transactions must be from {str(date)} onward.'
        else:
            self._message = f'Cannot apply interest and fees again in the month of {month}.'
        super().__init__(self._message)
    def __str__(self) -> str:
        return super().__str__()
    def __repr__(self) -> str:
        return f'TransactionSequenceError: {self._message}'

class TransactionLimitError(ValueError):
    """ When the daily/monthly transaction limit in a SavingsAccount() is reached"""
    def __init__(self, flag: bool) -> None:
        # True - daily limit
        # False - monthly limit
        if (flag):
            self._message = "This transaction could not be completed because this account already has 2 transactions in this day."
        else:
            self._message = "This transaction could not be completed because this account already has 5 transactions in this month."
        super().__init__(self._message)
    def __repr__(self) -> str:
        return f'TransactionLimitError: {self._message}'
    