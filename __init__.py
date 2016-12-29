# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

from trytond.pool import Pool
import account
import journal
import move
import statement
import reconciliation

def register():
    Pool.register(
        journal.BankJournal,
        statement.Statement,
        statement.StatementLine,
        reconciliation.AccountBankReconciliation,
        move.Line,
        move.Move,
        account.Account,
        move.OpenBankReconcileLinesStart,
        module='account_bank_statement', type_='model')
    Pool.register(
        move.OpenBankReconcileLines,
        module='account_bank_statement', type_='wizard')
