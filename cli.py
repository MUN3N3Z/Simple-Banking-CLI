from bank import Bank
from checkingAccount import CheckingAccount
from pickle import dump, load
from decimal import Decimal, InvalidOperation
from datetime import datetime
from utils import OverdrawError, TransactionSequenceError, TransactionLimitError
import logging
from decimal import Decimal
import sqlalchemy
from sqlalchemy.orm.session import sessionmaker
from database import Base

# Configure console logging
logging.basicConfig(
    # Set the minimum log level
    level=logging.DEBUG, 
    format='%(asctime)s|%(levelname)s|%(message)s',
    datefmt='%Y-%m-%d %I:%M:%S',
    handlers=[
        logging.FileHandler('bank.log'),
    ]
)

class BankCLI():
    """ Display menu options for banking services """
    def __init__(self) -> None:
        self._choices = {
            "1": self._open_account,
            "2": self._summary,
            "3": self._select_account,
            "4": self._add_transaction,
            "5": self._list_transactions,
            "6": self._interest_and_fees,
            "7": self._quit,
        }
        # Selected account number
        self._current_account = None
        # SQL db session
        self.session = Session()
        # Get bank from db
        self._bank = self.session.query(Bank).first()
        # Create and add Bank instance to db if not found
        if (not self._bank):
            self._bank = Bank()
            self.session.add(self._bank)
            self.session.commit()
            logging.debug(f'Saved to bank.db')
        else:
            logging.debug(f'Loaded from bank.db')
    def run(self):
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
            "quit",
        ]
        try:
            account = self._bank.find_account(self._current_account)
        except IndexError:
            account = self._current_account = None
            print("Please enter a valid account number.")
        finally:
            print("--------------------------------")
            # Display currently selected account
            if (self._current_account):
                if (isinstance(self._bank.find_account(self._current_account), (CheckingAccount))):
                    print("Currently selected account: Checking#{0},\tbalance: ${1}".format(f'{self._current_account:09d}', f'{self._bank.account_balance(self._current_account):,.2f}'))
                else:
                    print("Currently selected account: Savings#{0},\tbalance: ${1}".format(f'{self._current_account:09d}', f'{self._bank.account_balance(self._current_account):,.2f}'))  
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
            account_number = self._bank.create_checking_account(self.session)
            logging.debug(f'Created account: {account_number}')
            # Save new account 
            self.session.commit()
            logging.debug(f'Saved to bank.db')
        elif (account_type == "savings"):
            account_number = self._bank.create_savings_account(self.session)
            logging.debug(f'Created account: {account_number}')
            # Save new account 
            self.session.commit()
            logging.debug(f'Saved to bank.db')
        else:
            print("Please enter a valid account type")
        
        return
        
    def _summary(self):
        self._bank.summarize_accounts()
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
                logging.debug(f'Created transaction: {self._current_account}, {amount}')     
                self._bank.transact(self._current_account, amount, date, self.session)
                # Save new transaction
                self.session.commit()
                logging.debug(f'Saved to bank.db')
            except OverdrawError:
                print("This transaction could not be completed due to an insufficient account balance.")
            except TransactionLimitError as e2:
                print(e2)
            except TransactionSequenceError as e:
                print(e)
        return
        
    def _list_transactions(self):
        """ Print out all transactions for an account, sorted by date """
        try:
            self._bank.list_transactions(self._current_account)
        except TypeError:
            print("This command requires that you first select an account.")
        return

    def _interest_and_fees(self):
        """ Apply interest and fees to respective accounts """
        try:
            self._bank.apply_interest_fees(self._current_account, self.session)
            if (isinstance(self._bank.find_account(self._current_account), (CheckingAccount))):
                # Log interest
                logging.debug(f'Created transaction: {self._current_account}, {(Decimal(0.0008) * (self._bank.find_account(self._current_account).balance))}') 
            else:
                # Log interest
                logging.debug(f'Created transaction: {self._current_account}, {(Decimal(0.0041) * (self._bank.find_account(self._current_account).balance))}') 
            logging.debug(f'Triggered interest and fees')
            # Save new interest/fees transaction 
            self.session.commit()
            logging.debug(f'Saved to bank.db')
        except TransactionSequenceError as e:
            print(e)
        return 
    # Save/Load functions are obsolete now that we have a db
    
    def _quit(self):
        """ Leave the CLI """
        exit(0)

if __name__ == "__main__":
    # Catch unhandled non-system errors
    try:
        # Connect to the database
        engine = sqlalchemy.create_engine("sqlite:///bank.db")
        # Create SQL tables based on OOP models
        # if the tables already exist, this does nothing (even if there was a change)
        Base.metadata.create_all(engine)
        # Session factory
        Session = sessionmaker(bind=engine)

        BankCLI().run()
    except (EOFError):
        print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
        logging.error("EOFError: 'EOF when reading a line'")
    except (OverdrawError, TransactionSequenceError, TransactionLimitError) as e:
        print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
        logging.error(repr(e))
    exit(0)