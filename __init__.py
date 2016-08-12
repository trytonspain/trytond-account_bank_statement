# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

from trytond.pool import Pool
from .statement import *
from .move import *
from .reconciliation import *
from .account import *
from .journal import *


def register():
    Pool.register(
        BankJournal,
        Statement,
        StatementLine,
        AccountBankReconciliation,
        Line,
        Move,
        Account,
        OpenBankReconcileLinesStart,
        module='account_bank_statement', type_='model')
    Pool.register(
        OpenBankReconcileLines,
        module='account_bank_statement', type_='wizard')
