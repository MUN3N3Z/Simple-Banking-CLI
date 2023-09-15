from sys import exit
from checkingAccount import CheckingAccount
from savingsAccount import SavingsAccount

class Bank():
    """ Top-level management class """
    def __init__(self) -> None:
        # List of all accounts in chronological order
        self._accounts = []
    def _create_checking_account(self) -> None:
        """ Creates an instance of a Savings account object and appends it to the accounts list"""
        account_number = len(self._accounts) + 1
        new_checking_account = CheckingAccount(account_number)
        self._accounts.append(new_checking_account)
        return account_number

    def _create_savings_account(self) -> int:
        """ Creates an instance of a Savings account object and appends it to the accounts list"""
        account_number = len(self._accounts) + 1
        new_savings_account = SavingsAccount(account_number)
        self._accounts.append(new_savings_account)
        return account_number
    
    def _account_balance(self, account_number:int) -> int:
        """ Return account balance for account with account number: account_number """
        return self._accounts[account_number - 1].balance
    
    def _find_account(self, account_number:int):
        """ Return an instance of an account object with account_number """
        return self._accounts[account_number - 1]
    
    def _print_account_summary(self, account_number:int) -> None:
        """ Print account types, numbers and balances """
        if (isinstance(self._accounts[account_number - 1], (CheckingAccount))):
            print("Checking#{0},\tbalance: ${1}".format(f'{account_number:09d}', f'{self._account_balance(account_number):,.2f}'))
        else:
            print("Savings#{0},\tbalance: ${1}".format(f'{account_number:09d}', f'{self._account_balance(account_number):,.2f}'))   

    def _summarize_accounts(self) -> None:
        """ Print account types, numbers and balances for all accounts"""
        for account in self._accounts:
            self._print_account_summary(account._get_account_number())   

    def _transact(self, account_number:int, amount:str, date: str) -> None:
        """ Process a transaction """
        self._accounts[account_number - 1]._process_transaction(amount, date)
        return
    
    def _list_transactions(self, account_number:int) -> None:
        self._accounts[account_number - 1]._print_transactions()

    def _apply_interest_fees(self, account_number:int) -> None:
        """ Apply interest and fees to respective accounts """
        self._accounts[account_number - 1]._compute_interest_fees()
