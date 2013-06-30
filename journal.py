#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta

__metaclass__ = PoolMeta
__all__ = ['BankJournal']


class BankJournal(ModelSQL, ModelView):
    'Bank Statement Journal'
    __name__ = 'account.bank.statement.journal'
    name = fields.Char('Name', required=True)
    journal = fields.Many2One('account.journal', 'Journal', required=True,
        domain=[('type', '=', 'bank_statement')])
    currency = fields.Many2One('currency.currency', 'Currency', required=True)
    company = fields.Many2One('company.company', 'Company', required=True,
            select=True)

    @classmethod
    def __setup__(cls):
        super(BankJournal, cls).__setup__()
        cls._error_messages.update({
            'currency_modify': ('You cannot modify the currency to journal '
            'that already has a statement on date %(date)s')})

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
    def write(cls, journals, vals):
        if not 'currency' in vals:
            return super(BankJournal, cls).write(journals, vals)

        Statement = Pool().get('account.bank.statement')
        for journal in journals:
            statements = Statement.search([('journal', '=', journal),
                ('state', 'in', ['confirmed', 'posted'])], limit=1)
            if not statements:
                continue
            statement, = statements
            cls.raise_user_error('currency_modify', {'date': statement.date})

        return super(BankJournal, cls).write(journals, vals)
