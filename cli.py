from bank import Bank
from checkingAccount import CheckingAccount
from pickle import dump, load
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
        print("--------------------------------")
        # Display currently selected account
        if (self._current_account):
            if (isinstance(self._bank._find_account(self._current_account), (CheckingAccount))):
                print("Currently selected account: Checking#{0}, balance: ${1}".format(f'{self._current_account:09d}', f'{self._bank._account_balance(self._current_account):,.2f}'))
            else:
                print("Currently selected account: Savings#{0}, balance: ${1}".format(f'{self._current_account:09d}', f'{self._bank._account_balance(self._current_account):,.2f}'))   
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
            self._bank._create_checking_account()
        else:
            self._bank._create_savings_account()
        return
        
    def _summary(self):
        self._bank._summarize_accounts()
        return
    
    def _select_account(self) -> None:
        """ Select an individual account """
        print("Enter account number")
        self._current_account = int(input(">"))
        return

    def _add_transaction(self) -> None:
        """ Register a transaction with selected account """
        # Get user input for transaction details
        print("Amount?")
        amount = input(">")
        print("Date? (YYYY-MM-DD)")
        date = input(">")
        self._bank._transact(self._current_account, amount, date)
        return
        
    def _list_transactions(self):
        """ Print out all transactions for an account, sorted by date """
        self._bank._list_transactions(self._current_account)
        return

    def _interest_and_fees(self):
        """ Apply interest and fees to respective accounts """
        self._bank._apply_interest_fees(self._current_account)
        return 
    
    def _save(self):
        """ Pickle the bank object """
        # Pickle bank object
        with open("bank.pkl", "wb") as file:
            dump(self._bank, file)
        return
    
    def _load(self):
        # Load pickled object
        with open("bank.pkl", "rb") as file:
            self._bank = load(file)
        self._current_account = None
        return
    
    def _quit(self):
        """ Leave the CLI """
        exit(0)

if __name__ == "__main__":
    BankCLI()._run()