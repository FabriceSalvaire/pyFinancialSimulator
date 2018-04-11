from FinancialSimulator.Accounting.BackendStore.MongoDB import AccountingStore
accounting_store = AccountingStore()

# for journal_entry in accounting_store.find_journal_entry('JOD'):
#     print(journal_entry)

for account_snapshot in accounting_store.find_account_snapshot(512):
    print(account_snapshot)
