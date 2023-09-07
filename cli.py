from bank import Bank

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
    def _run(self):
        """ Display menu and respond to choices"""
        while (True):
            self._display_menu()
            # Get user input and execute
            choice = input("> ")
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
        print("Currently selected account: ")
        for i,j in enumerate(command_items):
            if (i == 0):
                # Print first non-command without index
                print(command_items[0])
            else:
                # Print rest of command options with indices
                print(f"{i}: {j}")

    def _open_account(self):
        pass
    def _summary(self):
        pass
    def _select_account(self):
        pass
    def _add_transaction(self):
        pass
    def _list_transactions(self):
        pass
    def _interest_and_fees(self):
        pass
    def _save(self):
        pass
    def _load(self):
        pass
    def _quit(self):
        """ Leave the CLI """
        exit(0)

if __name__ == "__main__":
    BankCLI()._run()