# OS - MacOS
import tkinter as tk
import sys
import logging
import sqlalchemy
from database import Base
from sqlalchemy.orm.session import sessionmaker
from utils import OverdrawError, TransactionSequenceError, TransactionLimitError
from bank import Bank
from datetime import datetime
from decimal import Decimal, InvalidOperation
from checkingAccount import CheckingAccount
from tkinter import ttk, messagebox
from tkcalendar import Calendar

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
        # self._window.report_callback_exception = self._handle_exception # Register error-handling function with the tk-window

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

        # Window options frame
        self._options_frame = tk.Frame(self._window)
        self._options_frame.grid(row=1, column=1, columnspan=2)
        # Option frame buttons
        tk.Button(self._options_frame, 
                  text="Open Account",
                  command=self._open_account).grid(row=1, column=1)
        tk.Button(self._options_frame,
                  text="Add Transaction",
                  command=self._add_transaction).grid(row=1, column=2)
        tk.Button(self._options_frame,
                  text="Interest and Fees",
                  command=self._interest_and_fees).grid(row=1, column=3)
        # List of account radio buttons
        self._radiobuttons = []
        # Display account summaries
        self._display_accounts()
        # Create a Text widget
        self._current_account_widget = tk.Text(self._window, wrap=tk.WORD, state=tk.NORMAL, width=70, height=1)
        self._current_account_widget.grid(row=0, column=1)
        self._current_account_widget.insert("1.0", "Currently selected account: None")
        self._current_account_widget.config(state=tk.DISABLED) # Prevent user from directly inserting text
        # Display account transactions
        self._listbox = None

        self._window.mainloop()
    
    def _select_account(self, index:int) -> None:
        """ Select an individual account """
        account_summaries = self._bank.return_accounts()
        self._current_account = index + 1
        self._current_account_widget.config(state=tk.NORMAL)
        # Delete displayed "current account"
        self._current_account_widget.delete("1.0", tk.END)
        text = "Currently selected account: " + account_summaries[index]
        # Display new current account
        self._current_account_widget.insert("1.0", text)
        self._current_account_widget.config(state=tk.DISABLED)
        # Display transactions for selected account
        self._display_transactions()
        return
           
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

    def _add_transaction(self) -> None:
        """ Register a transaction with selected account """
        popup = tk.Toplevel(self._window)
        popup.title("Create a new transaction")
        # Date picker
        date_label = ttk.Label(popup, text="Select Date:")
        date_label.pack()
        calendar = Calendar(popup, selectmode="day", date_pattern= "y-mm-dd")
        calendar.pack()
        # Amount entry
        amount_label = ttk.Label(popup, text="Enter amount: ")
        amount_label.pack()
        amount_var = tk.StringVar()
        amount_entry = ttk.Entry(popup, textvariable=amount_var, validate="none")
        amount_entry.pack()
        # Amount validation 
        def transact():
            # Ensure an account is selected
            if (not self._current_account):
                messagebox.showerror("Error", "This command requires that you first select an account")
                popup.destroy()
            else:
                amount = Decimal()
                try: 
                    amount = Decimal(amount_var.get())
                except InvalidOperation:
                    messagebox.showerror("Error", "Please try again with a valid dollar amount.")
                else:
                    # Process the transaction with valid inputs
                    try:
                        logging.debug(f'Created transaction: {self._current_account}, {amount}') 
                        date = datetime.strptime(calendar.get_date(), "%Y-%m-%d").date()    
                        self._bank.transact(self._current_account, amount, date, self.session)
                        # Save new transaction
                        self.session.commit()
                        logging.debug(f'Saved to bank.db')
                        popup.destroy()
                        # Refresh transactions
                        self._display_transactions()
                        # Refresh Current Account widget
                        self._select_account(self._current_account - 1)
                        
                    except OverdrawError:
                        messagebox.showerror("Error", "This transaction could not be completed due to an insufficient account balance.")
                    except TransactionLimitError as e2:
                        messagebox.showerror("Error", repr(e2))
                    except TransactionSequenceError as e:
                        messagebox.showerror("Error", repr(e))
        # Submit button
        submit_button = ttk.Button(popup, text="Submit", command=lambda: transact())
        submit_button.pack()
        return

    def _interest_and_fees(self):
        """ Apply interest and fees to respective accounts """
        # Ensure an account is selected
        if (not self._current_account):
            messagebox.showerror("Error", "This command requires that you first select an account")
        else:
            try:
                self._bank.apply_interest_fees(self._current_account, self.session)
                logging.debug(f'Triggered interest and fees')
                if (isinstance(self._bank.find_account(self._current_account), (CheckingAccount))):
                    # Log interest
                    logging.debug(f'Created transaction: {self._current_account}, {(Decimal(0.0008) * (self._bank.find_account(self._current_account).balance))}') 
                else:
                    # Log interest
                    logging.debug(f'Created transaction: {self._current_account}, {(Decimal(0.0041) * (self._bank.find_account(self._current_account).balance))}') 
                # Save new interest/fees transaction 
                self.session.commit()
                logging.debug(f'Saved to bank.db')
                # Refresh transactions
                self._display_transactions()
            except TransactionSequenceError as e:
                messagebox.showerror("Error", repr(e))
        return 
    
    def _display_transactions(self) -> None:
        # Get transactions for currently-selected account
        account_transactions = self._bank.return_transactions(self._current_account)
        # Create transaction labels
        transactions_heading_label = tk.Label(self._window, text="Transactions", font="Helvetica 18 bold") # Transactions heading
        transactions_heading_label.grid(row=0, column=6)
        for i,j in enumerate(account_transactions):
            label = (tk.Label(self._window, text=j[0], fg="green") if (j[1]) else tk.Label(self._window, text=j[0], fg="red"))
            label.grid(row=i+1, column=6)
        return
    
    def _display_accounts(self):
        """ Display a list of accounts and their balances as radio buttons """
        # Destroy current radio buttons to create space for new one
        if (self._radiobuttons):
            for rb in self._radiobuttons:
                rb.destroy()
            self._radiobuttons = []
        # Get account summaries
        account_summaries = self._bank.return_accounts()
        selected_item = tk.StringVar()
        accounts_heading_label = tk.Label(self._window, text="Accounts", font="Helvetica 18 bold") # Accounts heading
        accounts_heading_label.grid(row=0, column=5)
        # Create a list of account radio buttons and pack them into the listbox
        for i,j in enumerate(account_summaries):
            rb = tk.Radiobutton(self._window, text=j, 
                                variable=selected_item, value=j, 
                                command=lambda i=i: self._select_account(i))
            rb.grid(row=i+1, column=5)
            self._radiobuttons.append(rb)
        return

    def _handle_exception(exception, value, traceback):
        """ Defines a callback function that handles exceptions """
        print("Sorry! Something unexpected happened. If this problem persists please contact our support team for assistance.")
        logging.error(f"{exception.__name__}: {repr(value)}")
        sys.exit(0)


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