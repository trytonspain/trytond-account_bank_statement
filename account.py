#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Account']


class Account:
    __metaclass__ = PoolMeta
    __name__ = 'account.account'

    bank_reconcile = fields.Boolean('Bank Conciliation')

    @staticmethod
    def default_bank_reconcile():
        return False
