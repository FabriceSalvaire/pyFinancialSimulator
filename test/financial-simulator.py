####################################################################################################

import datetime

####################################################################################################

def date_iterator(start, stop, delta):
    date = start
    while date < stop:
        yield date
        date += delta

####################################################################################################

class JournalEntry:

    ##############################################

    def __init__(self, source, description=''):

        self._source = source
        self._description = description

    ##############################################

    @property
    def source(self):
        return self._source

    ##############################################

    @property
    def description(self):
        return self._description

####################################################################################################

class SimpleJournalEntry(JournalEntry):

    ##############################################

    def __init__(self, source, destination, amount, description=''):

        super().__init__(source, description)
        self._destination = destination
        self._amount = amount

    ##############################################

    @property
    def destination(self):
        return self._destination

    ##############################################

    @property
    def amount(self):
        return self._amount

    ##############################################

    def is_debit_for(self, account):
        return self._source is account

    ##############################################

    def is_credit_for(self, account):
        return self._destination is account

####################################################################################################

class JournalEntryDistribution:

    ##############################################

    def __init__(self, destination, amount):

        self._destination = destination
        self._amount = amount

    ##############################################

    @property
    def destination(self):
        return self._destination

    ##############################################

    @property
    def amount(self):
        return self._amount

####################################################################################################

class DistributedJournalEntry(JournalEntry):

    ##############################################

    def __init__(self, source, description='', *args):

        super().__init__(source, description)
        self._distribution = args

    ##############################################

    def __iter__(self):

        for item in self._distribution:
            yield SimpleJournalEntry(self._source, item.destination, item.amount, self._description)

    ##############################################

    @property
    def amount(self):
        # Fixme: cache ?
        return sum([item.amount for item in self._distribution])

####################################################################################################

class Account:

    ##############################################

    def __init__(self, code, name, parent = None, initial_balance=0):

        self._name = name
        self._code = code
        
        self._parent = parent
        self._childs = set()
        parent.add_child(self)
        
        self._journal = []
        self._initial_balance = initial_balance
        
        self._inner_credit = None
        self._inner_debit = None
        self._inner_balance = None
        
        self._credit = None
        self._debit = None
        self._balance = None

    ##############################################

    @property
    def name(self):

        return self._name

    ##############################################

    @property
    def code(self):

        return self._code

    ##############################################

    def add_child(self, child):

        self.balance_is_dirty()
        self._childs.add(child)

    ##############################################

    @property
    def parent(self):

        return self._parent

    ##############################################

    def balance_is_dirty(self):

        self._balance = None

    ##############################################

    def inner_balance_is_dirty(self):

        self._inner_balance = None
        self.balance_is_dirty()

    ##############################################

    def _parent_is_dirty(self):

        if self._parent is not None:
            self._parent.balance_is_dirty()

    ##############################################

    def _compute_balance(self):

        if self._inner_balance is None:
            self._inner_credit = 0
            self._inner_debit = 0
            for transaction in self._journal:
                self._run_transaction(transaction)
            self._inner_balance = self._inner_credit - self._inner_debit
        
        if self._balance is None:
            self._credit = self._inner_credit
            self._debit = self._inner_debit
            for child in self._childs:
                self._credit += child.credit
                self._debit += child.debit
            self._balance = self._credit - self._debit

    ##############################################

    @property
    def balance(self):

        if self._balance is None:
            self._compute_balance()
        return self._balance

    ##############################################

    @property
    def credit(self):

        if self._balance is None:
            self._compute_balance()
        return self._credit

    ##############################################

    @property
    def debit(self):

        if self._balance is None:
            self._compute_balance()
        return self._debit

    ##############################################

    def _run_simple_transaction(self, transaction):

        if transaction.is_debit_for(self):
            self._inner_debit += transaction.amount
        elif transaction.is_credit_for(self):
            self._inner_credit += transaction.amount
        else:
            raise NameError("transaction don't involve the account")

    ##############################################

    def _run_transaction(self, transaction):

        self._parent_is_dirty()
        if isinstance(transaction, DistributedJournalEntry):
            for item in transaction:
                self._run_simple_transaction(item)
        else:
            self._run_simple_transaction(transaction)

    ##############################################

    def log_transaction(self, transaction):

        self._journal.append(transaction)
        self._run_transaction(transaction)

    ##############################################

    def log_debit(self, destination, amount, description=''):

        transaction = SimpleJournalEntry(self, destination, amount, description)
        self.log_transaction(transaction)
        destination.log_transaction(transaction)

    ##############################################

    def log_credit(self, source, amount, description=''):

        transaction = SimpleJournalEntry(source, self, amount, description)
        self.log_transaction(transaction)
        source.log_transaction(transaction)

####################################################################################################

class Journal:

    ##############################################

    def __init__(self, name):

        self._name = name

    ##############################################

    @property
    def name(self):

        return self._name

####################################################################################################

# year = 2016
# start_day = datetime.date(year, 1, 1)
# stop_day = datetime.date(year +1, 1, 1)
# day_timedelta = datetime.timedelta(1)

# for date in date_iterator(start_day, stop_day, day_timedelta):
#     print(date.toordinal())

####################################################################################################

# Plan comptable Français :
#  44571 TVA collectée
#  701 Ventes de produits finis
#  702 Ventes de produits intermédiaires
#  703 Ventes de produits résiduels
#  706 Prestations de services
#  707 Ventes de marchandises

# Enregistrement d'une vente
#  débit 512 Banques
#  crédit 7 Ventes
#  crédit 44571 TVA collectée

bank_account = Account(512, 'Compte Bancaire')

####################################################################################################
#
# End
#
####################################################################################################
