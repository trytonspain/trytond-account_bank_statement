#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.pool import Pool
from . import statement
from . import journal


def register():
    Pool.register(
        journal.BankJournal,
        statement.Statement,
        statement.StatementLine,
        statement.ImportStart,
        module='account_bank_statement', type_='model')
    Pool.register(
        statement.Import,
        module='account_bank_statement', type_='wizard')
