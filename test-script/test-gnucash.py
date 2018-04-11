####################################################################################################

import datetime
import os

####################################################################################################

import FinancialSimulator.Logging.Logging as Logging

logger = Logging.setup_logging('financial-simulator')
_module_logger = logger

####################################################################################################

from FinancialSimulator.Accounting.AccountChart import AccountChart, Account
from FinancialSimulator.Accounting.AccountBalanceHistory import AccountBalanceWithHistory
from FinancialSimulator.Accounting.Error import UnbalancedEntryError, DuplicatedEntryError
from FinancialSimulator.Accounting.FinancialPeriod import (FinancialPeriod,
                                                           AccountChartBalance,
                                                           Journals)
from FinancialSimulator.Accounting.Journal import Imputation, DebitImputationData, CreditImputationData

from FinancialSimulator.Accounting.JournalInMemory import JournalInMemory
from FinancialSimulator.Importer.Gnucash import GnucashDataBase

####################################################################################################

class DatabaseConfig:

    hostname = 'localhost'
    database = 'gnucash'
    user_name = 'gnucash'
    password = 'gnucash'

####################################################################################################

def renumber_node(root_node, prefix=''):

    siblings = list(root_node)
    siblings.sort(key=lambda node: node.description)
    pattern = '{}' + '{:0%u}' % len(str(len(siblings)))
    for i, node in enumerate(siblings):
        number = int(pattern.format(prefix, i +1))
        node._number = number
        if node.has_siblings():
            renumber_node(node, number)
    root_node.sort_siblings()

####################################################################################################

gnucash_database = GnucashDataBase(DatabaseConfig)
accounts_table = gnucash_database.accounts_table
accounts_row_class = gnucash_database._accounts_row_class
splits_table = gnucash_database.splits_table
transactions_table = gnucash_database.transactions_table
transactions_row_class = gnucash_database._transactions_row_class

####################################################################################################

# Make nodes
accounts_guid = {}
roots = []
for i, row in enumerate(accounts_table.query()):
    guid = i +1 # fake number
    account = Account(guid, row.name, comment=row.description)
    accounts_guid[row.guid] = account
    if not row.parent_guid:
        roots.append(account)

# Make hierarchy
for row in accounts_table.query():
    if row.parent_guid:
        account = accounts_guid[row.guid]
        parent = accounts_guid[row.parent_guid]
        account.parent = parent

# Renumber
for account in roots:
    if account.description == 'Root Account':
        account._number = 1
        root_account = account
        break
roots.remove(root_account)
for i, account in enumerate(roots):
    account._number = i +2
renumber_node(root_account, prefix=1)

# for account in root_account.depth_first_search():
#     print('    '*account.level(), account, account.description)

account_chart = AccountChart(name='gnucash')
for account in accounts_guid.values():
    account_chart.add_node(account)
# for account in account_chart:
#     print('    '*account.level(), account, account.description)

####################################################################################################

journal_definitions = (
    ('JOD', 'Journal des opérations diverses'),
)

# Fixme:
start_date = datetime.date(1990, 1, 1)
stop_date = datetime.date(2016, 12, 31)

class MyAccountChartBalance(AccountChartBalance):
    __account_balance_factory__ = AccountBalanceWithHistory

class MyJournals(Journals):
    __journal_factory__ = JournalInMemory

class MyFinancialPeriod(FinancialPeriod):
    __account_chart_factory__ = MyAccountChartBalance
    __analytic_account_chart_factory__ = MyAccountChartBalance
    __journals_factory__ = MyJournals

# Fixme
analytic_account_chart = None

financial_period_class = MyFinancialPeriod
financial_period = financial_period_class(account_chart,
                                          analytic_account_chart,
                                          journal_definitions,
                                          start_date, stop_date)
account_chart = financial_period.account_chart
analytic_account_chart = financial_period.analytic_account_chart
journals = financial_period.journals
journal = journals['JOD']

####################################################################################################

class ImputationListener:
    def slot(self, signal, sender, **kwargs):
        imputation = sender
        imputation.account.history.save(imputation)
        if imputation.analytic_account is not None:
            imputation.analytic_account.history.save(imputation)

imputation_listener = ImputationListener()
# global
Imputation.imputed.connect(imputation_listener.slot)

####################################################################################################

query = transactions_table.query().order_by(transactions_row_class.post_date)
for row in query:
    # print('', '-'*100)
    # print(row.post_date, row.description)
    imputations = []
    for split in row.splits:
        value = split.value
        account = accounts_guid[split.account_guid]
        if value > 0:
            factory = CreditImputationData
        else:
            factory = DebitImputationData
        imputation = factory(account.number, abs(value), None, resolved=False)
        imputations.append(imputation)
        # print(split.to_dict())
        # print('  ', account.description, split.value, '€') # , split.quantity
    try:
        journal.log_entry(row.post_date.date(), row.description, imputations)
    except (UnbalancedEntryError, DuplicatedEntryError) as e:
        # Compte Soldes initiaux
        # UnbalancedEntryError 1998-03-31 Elanciel France
        # DuplicatedEntryError 1999-07-16 (Soldes initiaux -> Soldes initiaux)
        # UnbalancedEntryError 1999-07-16
        # Fixme: transactions réparties / erreurs ?
        print(type(e), row.post_date, row.description,
              [account_chart[imputation.account].description for imputation in imputations])

# For Ctrl+C
del gnucash_database

####################################################################################################

if True:
    from FinancialSimulator.WebApplication.Application import create_application

    # Fixme: if DEBUG = True then reload ...
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    application = create_application(config_path, account_chart, analytic_account_chart, journals)
    application.run()
