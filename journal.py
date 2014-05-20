#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from sql import Literal

from trytond.model import ModelView, ModelSQL, fields
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta

__metaclass__ = PoolMeta
__all__ = ['Journal', 'BankJournal']


class Journal:
    __name__ = 'account.journal'

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().cursor
        sql_table = cls.__table__()

        super(Journal, cls).__register__(module_name)
        cursor.execute(*sql_table.update(
                columns=[sql_table.type],
                values=[Literal('cash')],
                where=sql_table.type == Literal('bank_statement')))


class BankJournal(ModelSQL, ModelView):
    'Bank Statement Journal'
    __name__ = 'account.bank.statement.journal'
    name = fields.Char('Name', required=True)
    journal = fields.Many2One('account.journal', 'Journal', required=True,
        domain=[('type', '=', 'cash')])
    currency = fields.Many2One('currency.currency', 'Currency', required=True)
    company = fields.Many2One('company.company', 'Company', required=True,
            select=True)

    @classmethod
    def __setup__(cls):
        super(BankJournal, cls).__setup__()
        cls._error_messages.update({
                'currency_modify': ('You cannot modify the currency to '
                    'journal that already has a statement on date %s'),
                'journal_accounts_not_banc_reconcile': (
                    'The Default Credit or Debit accounts of Journal '
                    '"%(journal)s", related to Bank Journal '
                    '"%(bank_journal)s", are not configured as '
                    '"Bank conciliation".'),
                })

    @staticmethod
    def default_currency():
        if Transaction().context.get('company'):
            Company = Pool().get('company.company')
            company = Company(Transaction().context['company'])
            return company.currency.id

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @classmethod
    def validate(cls, journals):
        super(BankJournal, cls).validate(journals)
        cls.check_journal_accounts(journals)

    @classmethod
    def check_journal_accounts(cls, journals):
        for journal in journals:
            if (not journal.journal.credit_account or
                not journal.journal.credit_account.bank_reconcile or
                    not journal.journal.debit_account or
                    not journal.journal.debit_account.bank_reconcile):
                cls.raise_user_error('journal_accounts_not_banc_reconcile', {
                        'journal': journal.journal.rec_name,
                        'bank_journal': journal.rec_name,
                        })

    @classmethod
    def write(cls, *args):
        Statement = Pool().get('account.bank.statement')
        actions = iter(args)
        args = []
        for journals, values in  zip(actions, actions):
            if 'currency' not in values:
                super(BankJournal, cls).write(journals, values)
                continue

            for journal in journals:
                statements = Statement.search([('journal', '=', journal),
                    ('state', 'in', ['confirmed', 'posted'])], limit=1)
                if not statements:
                    continue
                statement, = statements
                cls.raise_user_error('currency_modify', statement.date)
            args.extend((journals, values))

        super(BankJournal, cls).write(*args)
