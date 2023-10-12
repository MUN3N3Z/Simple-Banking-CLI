from sys import exit
from checkingAccount import CheckingAccount
from savingsAccount import SavingsAccount
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer
from database import Base

class Bank(Base):
    """ Top-level management class """
    # Create a "Bank" table
    __tablename__ = "bank"
    # Id column on the "Bank" table
    _id = Column(Integer, primary_key=True)
    # Backref to accounts
    _accounts = relationship("Account", backref=backref("bank"))


    # def __init__(self) -> None:
    #     # List of all accounts in chronological order
    #     self._accounts = []
    def create_checking_account(self, session) -> int:
        """ Creates an instance of a Savings account object and appends it to the accounts list"""
        account_number = len(self._accounts) + 1
        new_checking_account = CheckingAccount(account_number)
        self._accounts.append(new_checking_account)
        session.add(new_checking_account)

        return account_number

    def create_savings_account(self, session) -> int:
        """ Creates an instance of a Savings account object and appends it to the accounts list"""
        account_number = len(self._accounts) + 1
        new_savings_account = SavingsAccount(account_number)
        self._accounts.append(new_savings_account)
        session.add(new_savings_account)

        return account_number
    
    def account_balance(self, account_number:int) -> int:
        """ Return account balance for account with account number: account_number """
        return self._accounts[account_number - 1].balance
    
    def find_account(self, account_number:int):
        """ Return an instance of an account object with account_number """
        if (account_number):
            return self._accounts[account_number - 1]
    
    def _print_account_summary(self, account_number:int) -> None:
        """ Print account types, numbers and balances """
        if (isinstance(self._accounts[account_number - 1], (CheckingAccount))):
            print("Checking#{0},\tbalance: ${1}".format(f'{account_number:09d}', f'{self.account_balance(account_number):,.2f}'))
        else:
            print("Savings#{0},\tbalance: ${1}".format(f'{account_number:09d}', f'{self.account_balance(account_number):,.2f}'))   

    def summarize_accounts(self) -> None:
        """ Print account types, numbers and balances for all accounts"""
        for account in self._accounts:
            self._print_account_summary(account.get_account_number())   

    def transact(self, account_number:int, amount:Decimal, date, session) -> None:
        """ Process a transaction """
        self._accounts[account_number - 1].process_transaction(amount, date, session)
        return
    
    def list_transactions(self, account_number:int) -> None:
        self._accounts[account_number - 1].print_transactions()

    def apply_interest_fees(self, account_number:int, session) -> None:
        """ Apply interest and fees to respective accounts """
        self._accounts[account_number - 1].compute_interest_fees(session)
