# OS - MacOS
import tkinter as tk
import logging
import sqlalchemy
from database import Base
from sqlalchemy.orm.session import sessionmaker
from utils import OverdrawError, TransactionSequenceError, TransactionLimitError
from bank import Bank
from datetime import datetime
from decimal import Decimal, InvalidOperation
from savingsAccount import SavingsAccount
from checkingAccount import CheckingAccount

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

class BankGUI:
    """ Display a bank menu and respond to choices when run """
    def __init__(self) -> None:
        # Initialize new bank gui window
        self._window = tk.Tk()
        self._window.title("MY BANK")

        # Selected account number
        self._current_account = None
        # SQL db session
        self.session = Session()
        # Get bank from db
        self._bank = self.session.query(Bank).first()
        logging.debug(f'Loaded from bank.db')
        # Create and add Bank instance to db if not found
        if (not self._bank):
            self._bank = Bank()
            self.session.add(self._bank)
            self.session.commit()
            logging.debug(f'Saved to bank.db')

        # Window options frame
        self._options_frame = tk.Frame(self._window)

        # Option frame buttons
        tk.Button(self._options_frame, 
                  text="Open Account",
                  command=self._open_account).grid(row=1, column=1)
        tk.Button(self._options_frame,
                  text="Select Account",
                  command=self._select_account).grid(row=1, column=2)
        tk.Button(self._options_frame,
                  text="Add Transaction",
                  command=self._add_transaction).grid(row=1, column=3)
        tk.Button(self._options_frame,
                  text="Interest and Fees",
                  command=self._interest_and_fees).grid(row=1, column=4)
        
        self._options_frame.grid(row=0, column=1, columnspan=2)
        
        # Account summaries will be displayed here
        self._listbox = None
        self._display_accounts()

        self._window.mainloop()
        
    def _open_account(self) -> None:
        """ Either open a savings or checkings account """
        popup = tk.Toplevel(self._window)
        popup.title("Open a new account")
        # Variable to store the selected option
        selected_option = tk.IntVar()
        # Radio buttons
        option1 = tk.Radiobutton(popup, text="Checking Account", variable=selected_option, value=1)
        option2 = tk.Radiobutton(popup, text="Savings Account", variable=selected_option, value=2)
        option1.pack()
        option2.pack()
        # Enter and Cancel buttons
        enter_button = tk.Button(popup, text="Enter", command=lambda:on_enter(popup, selected_option))
        cancel_button = tk.Button(popup, text="Cancel", command=popup.destroy)
        enter_button.pack()
        cancel_button.pack()
        # Callback button
        def on_enter(popup, selected_options):
            # Open checking account
            if selected_option.get() == 1:
                account_number = self._bank.create_checking_account(self.session)
                logging.debug(f'Created account: {account_number}')
                # Save new account 
                self.session.commit()
                logging.debug(f'Saved to bank.db')
            # Open savings account
            else:
                account_number = self._bank.create_savings_account(self.session)
                logging.debug(f'Created account: {account_number}')
                # Save new account 
                self.session.commit()
                logging.debug(f'Saved to bank.db')
            # Refresh accounts
            self._display_accounts()
            popup.destroy()
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
    
    def _interest_and_fees(self):
        """ Apply interest and fees to respective accounts """
        try:
            self._bank.apply_interest_fees(self._current_account, self.session)
            if (isinstance(self._bank.find_account(self._current_account), (CheckingAccount))):
                # Log interest
                logging.debug(f'Created transaction: {self._current_account}, {(Decimal(0.0008) * (self._bank.find_account(self._current_account).balance)).quantize(Decimal("0.00"))}') 
            else:
                # Log interest
                logging.debug(f'Created transaction: {self._current_account}, {(Decimal(0.0041) * (self._bank.find_account(self._current_account).balance)).quantize(Decimal("0.00"))}') 
            logging.debug(f'Triggered interest and fees')
            # Save new interest/fees transaction 
            self.session.commit()
            logging.debug(f'Saved to bank.db')
        except TransactionSequenceError as e:
            print(e)
        return 
    
    def _display_accounts(self):
        """ Display a list of accounts and their balances """
        if (self._listbox):
            self._listbox.destroy()
            print("Refreshed")
        account_summaries = self._bank._show_accounts()
        variable = tk.StringVar(value=account_summaries)
        # Create a Listbox to display the list
        self._listbox = tk.Listbox(self._options_frame, listvariable=variable)
        self._listbox.grid(row=1, column=5)
        self._listbox.config(width=30)
        print(account_summaries)
        return


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

        BankGUI()
    except (EOFError):
        print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
        logging.error("EOFError: 'EOF when reading a line'")
    except (OverdrawError, TransactionSequenceError, TransactionLimitError) as e:
        print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
        logging.error(repr(e))
    exit(0)