from bank import Bank
from checkingAccount import CheckingAccount
from pickle import dump, load
from decimal import Decimal, InvalidOperation
from datetime import datetime
from utils import OverdrawError, TransactionSequenceError, TransactionLimitError
import logging

# Configure console logging
logging.basicConfig(
    # Set the minimum log level
    level=logging.DEBUG, 
    format='%(asctime)s|%(levelname)s|%(message)s',
    datefmt='%m/%d/%Y %I:%M:%S',
    handlers=[
        logging.FileHandler('bank.log'),
    ]
)
class BankCLI():
    """ Display menu options for banking services """
    def __init__(self) -> None:
        # Create an instance of a bank to handle operations
        self._bank = Bank()
        self._choices = {
            "1": self._open_account,
            "2": self._summary,
            "3": self._select_account,
            "4": self._add_transaction,
            "5": self._list_transactions,
            "6": self._interest_and_fees,
            "7": self._save,
            "8": self._load,
            "9": self._quit,
        }
        # Selected account number
        self._current_account = None
    def _run(self):
        """ Display menu and respond to choices"""
        while (True):
            self._display_menu()
            # Get user input and execute
            choice = input(">")
            command = self._choices.get(choice)
            if (command): 
                command()
            else:
                # Invalid user choice
                print("{0} is not a valid choice.".format(choice))

    
    def _display_menu(self) -> None:
        command_items = [
            "Enter command",
            "open account",
            "summary",
            "select account",
            "add transaction",
            "list transactions",
            "interest and fees",
            "save",
            "load",
            "quit",
        ]
        try:
            account = self._bank._find_account(self._current_account)
        except IndexError:
            account = self._current_account = None
            print("Please enter a valid account number.")
        finally:
            print("--------------------------------")
            # Display currently selected account
            if (self._current_account):
                if (isinstance(self._bank._find_account(self._current_account), (CheckingAccount))):
                    print("Currently selected account: Checking#{0},\tbalance: ${1}".format(f'{self._current_account:09d}', f'{self._bank._account_balance(self._current_account):,.2f}'))
                else:
                    print("Currently selected account: Savings#{0},\tbalance: ${1}".format(f'{self._current_account:09d}', f'{self._bank._account_balance(self._current_account):,.2f}'))  
            else:
                print("Currently selected account: None")
            # Display menu items
            for i,j in enumerate(command_items):
                if (i == 0):
                    # Print first non-command without index
                    print(command_items[0])
                else:
                    # Print rest of command options with indices
                    print(f"{i}: {j}")
        return

    def _open_account(self) -> None:
        """ Either open a savings or checkings account """
        print("Type of account? (checking/savings)")
        account_type = input(">")
        if (account_type == "checking"):
            account_number = self._bank._create_checking_account()
            logging.debug(f'Created account: {account_number:09d}')
        elif (account_type == "savings"):
            account_number = self._bank._create_savings_account()
            logging.debug(f'Created account: {account_number:09d}')
        else:
            print("Please enter a valid account type")
        return
        
    def _summary(self):
        self._bank._summarize_accounts()
        return
    
    def _select_account(self) -> None:
        """ Select an individual account """
        print("Enter account number")
        try: 
            self._current_account = int(input(">"))
        except (ValueError):
            print("Please enter a valid account number.")
        return

    def _add_transaction(self) -> None:
        """ Register a transaction with selected account """
        # Get user input for transaction details
        amount = date = None
        while (not amount):
            print("Amount?")
            try: 
                amount = Decimal(input(">"))
            except InvalidOperation:
                print("Please try again with a valid dollar amount.")
        while (not date):
            print("Date? (YYYY-MM-DD)")
            try:
                date = datetime.strptime(input(">"), "%Y-%m-%d").date()
            except ValueError:
                print("Please try again with a valid date in the format YYYY-MM-DD.")
        # Account not selected
        if (not self._current_account):
            print("This command requires that you first select an account.")
        else:
            # Process the transaction with valid inputs
            try:
                self._bank._transact(self._current_account, amount, date)
                logging.debug(f'Created transaction: {self._current_account:09d}, {amount}')     
            except OverdrawError:
                print("This transaction could not be completed due to an insufficient account balance.")
            except TransactionSequenceError as e:
                print(e)
            except TransactionLimitError as e2:
                print(e2)
        return
        
    def _list_transactions(self):
        """ Print out all transactions for an account, sorted by date """
        try:
            self._bank._list_transactions(self._current_account)
        except TypeError:
            print("This command requires that you first select an account.")
        return

    def _interest_and_fees(self):
        """ Apply interest and fees to respective accounts """
        try:
            self._bank._apply_interest_fees(self._current_account)
            logging.debug(f'Triggered interest and fees')
        except TransactionSequenceError as e:
            print(e)
        return 
    
    def _save(self):
        """ Pickle the bank object """
        # Pickle bank object
        with open("bank.pkl", "wb") as file:
            dump(self._bank, file)
            logging.debug(f'Saved to bank.pickle')
        return
    
    def _load(self):
        # Load pickled object
        with open("bank.pkl", "rb") as file:
            self._bank = load(file)
            logging.debug(f'Loaded from bank.pickle')
        self._current_account = None
        return
    
    def _quit(self):
        """ Leave the CLI """
        exit(0)

if __name__ == "__main__":
    # Catch unhandled non-system errors
    try:
        BankCLI()._run()
    except (OverdrawError, TransactionSequenceError, TransactionLimitError) as e:
        print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
        logging.error(repr(e))
    exit(0)