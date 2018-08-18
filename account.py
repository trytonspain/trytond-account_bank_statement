#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['AccountTemplate', 'Account']


class AccountTemplate(metaclass=PoolMeta):
    __name__ = 'account.account.template'

    bank_reconcile = fields.Boolean('Bank Conciliation')

    @staticmethod
    def default_bank_reconcile():
        return False

    def _get_account_value(self, account=None):
        res = super(AccountTemplate, self)._get_account_value(account)

        res['bank_reconcile'] = self.bank_reconcile
        return res


class Account(metaclass=PoolMeta):
    __name__ = 'account.account'

    bank_reconcile = fields.Boolean('Bank Conciliation')

    @staticmethod
    def default_bank_reconcile():
        return False
