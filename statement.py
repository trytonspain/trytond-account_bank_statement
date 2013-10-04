#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.pyson import Eval, If, Not, Equal
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
import datetime

__metaclass__ = PoolMeta
__all__ = ['Statement', 'StatementLine']

CONFIRMED_STATES = {
    'readonly': Not(Equal(Eval('state'), 'draft'))
    }
CONFIRMED_DEPENDS = ['state']

POSTED_STATES = {
    'readonly': Not(Equal(Eval('state'), 'confirmed'))
    }
POSTED_DEPENDS = ['state']


class Statement(Workflow, ModelSQL, ModelView):
    'Bank Statement'
    __name__ = 'account.bank.statement'
    _rec_name = 'date'

    company = fields.Many2One('company.company', 'Company', required=True,
        select=True, domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', 0)),
            ])
    date = fields.DateTime('Date', required=True)
    journal = fields.Many2One('account.bank.statement.journal', 'Journal',
        required=True)
    lines = fields.One2Many('account.bank.statement.line', 'statement',
        'Lines')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('canceled', 'Canceled'),
            ], 'State', required=True, readonly=True)

    @classmethod
    def __setup__(cls):
        super(Statement, cls).__setup__()
        cls._transitions |= set((
                ('draft', 'confirmed'),
                ('confirmed', 'canceled'),
                ('canceled', 'draft'),
                ('draft', 'canceled'),
                ))
        cls._buttons.update({
                'confirm': {
                    'invisible': ~Eval('state').in_(['draft']),
                    'icon': 'tryton-go-next',
                    },
                'draft': {
                    'invisible': ~Eval('state').in_(['canceled']),
                    'icon': 'tryton-go-next',
                    },
                'cancel': {
                    'invisible': Eval('state').in_(['canceled']),
                    'icon': 'tryton-go-next',
                    },
                })

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_date():
        return datetime.datetime.now()

    @classmethod
    @ModelView.button
    @Workflow.transition('confirmed')
    def confirm(cls, statements):
        StatementLine = Pool().get('account.bank.statement.line')
        lines = []
        for statement in statements:
            lines += statement.lines
        StatementLine.confirm(lines)

    @classmethod
    @ModelView.button
    @Workflow.transition('canceled')
    def cancel(cls, statements):
        StatementLine = Pool().get('account.bank.statement.line')
        lines = []
        for statement in statements:
            for line in statement.lines:
                if not line.state in ('draft', 'canceled'):
                    line.raise_user_error('cannot_cancel_statement', {
                        'line': line.rec_name,
                        'state': line.state,
                    })
            lines += statement.lines
        StatementLine.cancel(lines)

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, statements):
        StatementLine = Pool().get('account.bank.statement.line')
        lines = []
        for statement in statements:
            for line in statement.lines:
                if not line.state in ('canceled', 'draft'):
                    raise "ups"
            lines += statement.lines
        StatementLine.cancel(lines)


class StatementLine(Workflow, ModelSQL, ModelView):
    'Bank Statement Line'
    __name__ = 'account.bank.statement.line'
    _order = [
        ('date', 'ASC'),
        ('sequence', 'ASC')
        ]
    _rec_name = 'description'

    statement = fields.Many2One('account.bank.statement', 'Statement',
        required=True, states=CONFIRMED_STATES)
    company = fields.Many2One('company.company', 'Company', required=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', 0)),
            ], select=True, states=CONFIRMED_STATES)
    date = fields.DateTime('Date', required=True, states=CONFIRMED_STATES)
    sequence = fields.Integer('Sequence')
    description = fields.Char('Description', required=True,
        states=CONFIRMED_STATES)
    amount = fields.Numeric('Amount', digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'], required=True, states=CONFIRMED_STATES)
    currency_digits = fields.Function(fields.Integer('currency digits'),
            'get_currency_digits')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('canceled', 'Canceled'),
            ('posted', 'Posted'),
            ], 'State', required=True, readonly=True)
    bank_lines = fields.One2Many('account.bank.reconciliation',
        'bank_statement_line', 'Bank Lines', domain=[
            ('account', 'in', (Eval('debit_account'), Eval('credit_account'))),
            ('bank_statement_line', 'in', (None, Eval('id'))),
            ], states=POSTED_STATES,
        depends=POSTED_DEPENDS + ['debit_account', 'credit_account', 'id'])
    credit_account = fields.Function(fields.Many2One('account.account',
            'Account'), 'get_accounts')
    debit_account = fields.Function(fields.Many2One('account.account',
            'Account'), 'get_accounts')
    reconciled = fields.Function(fields.Boolean('Reconciled'),
        'get_accounting_vals')
    moves_amount = fields.Function(fields.Numeric('Moves Amount',
            digits=(16, Eval('currency_digits', 2)),
            on_change_with=['bank_lines', 'state'],
            depends=['currency_digits']),
            'get_accounting_vals')
    journal = fields.Function(fields.Many2One('account.bank.statement.journal',
            'Journal'), 'get_journal', searcher='search_journal')
    statement_currency = fields.Function(fields.Many2One('currency.currency',
            'Statement Currency', depends=['statement', 'journal']),
            'get_statement_currency')
    company_currency = fields.Function(fields.Many2One('currency.currency',
            'Company Currency', depends=['statement', 'journal']),
            'get_company_currency')
    company_moves_amount = fields.Function(fields.Numeric('Moves Amount',
            digits=(16, Eval('company_currency_digits', 2)),
            on_change_with=['bank_lines'],
            depends=['company_currency_digits', 'bank_lines']),
            'get_accounting_vals')
    company_amount = fields.Function(fields.Numeric('Company Amount',
            digits=(16, Eval('company_currency_digits', 2)),
            depends=['company_currency_digits', 'amount']),
            'get_accounting_vals')
    company_currency_digits = fields.Function(
            fields.Integer('Company Currency Digits'),
            'get_company_currency_digits')

    @classmethod
    def __setup__(cls):
        super(StatementLine, cls).__setup__()
        cls._transitions |= set((
                ('draft', 'confirmed'),
                ('confirmed', 'posted'),
                ('posted', 'confirmed'),
                ('canceled', 'draft'),
                ('confirmed', 'canceled'),
                ('posted', 'canceled'),
                ))
        cls._buttons.update({
                'confirm': {
                    'invisible': ~Eval('state').in_(['draft', 'posted']),
                    'icon': 'tryton-go-next',
                    },
                'post': {
                    'invisible': Eval('state').in_([
                            'draft', 'canceled', 'posted']),
                    'icon': 'tryton-go-next',
                    },
                'cancel': {
                    'invisible': Eval('state').in_(['canceled']),
                    'icon': 'tryton-go-next',
                    },
                'draft': {
                    'invisible': ~Eval('state').in_(['canceled']),
                    },
                'search_reconcile': {
                    'invisible': ~Eval('state').in_(['confirmed']),
                    'icon': 'tryton-find',
                    },
                })
        cls._error_messages.update({
                'different_amounts': ('Moves Amount "%(moves_amount)s" does '
                    'not match Amount "%(amount)s" in line "%(line)s".'),
                'cannot_cancel_statement': ('Line "%(line)s" with state '
                '"%(state)s" can not be canceled. To cancel line ensure that '
                ' field "state" it is equal to "Canceled" or "Draft"')
                })

    def _search_bank_line_reconciliation(self):
        BankLines = Pool().get('account.bank.reconciliation')
        lines = BankLines.search([('amount', '=', self.company_amount)])
        if len(lines) == 1:
            line, = lines
            line.bank_statement_line = self
            line.save()

    def _search_reconciliation(self):
        self._search_bank_line_reconciliation()

    @classmethod
    @ModelView.button
    def search_reconcile(cls, st_lines):
        for st_line in st_lines:
            st_line._search_reconciliation()

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_state():
        return 'draft'

    def get_currency_digits(self, name):
        return self.statement_currency.digits

    def get_company_currency_digits(self, name):
        return self.company_currency.digits

    def get_statement_currency(self, name):
        return self.statement.journal.currency.id

    def get_company_currency(self, name):
        return self.statement.company.currency.id

    @classmethod
    def get_accounts(cls, lines, names):
        res = {}
        for name in names:
            res[name] = {}

        for line in lines:
            journal = line.statement.journal.journal
            for name in names:
                account = getattr(journal, name)
                res[name][line.id] = account and account.id
        return res

    @classmethod
    def get_accounting_vals(cls, lines, names):
        res = {}
        for name in names:
            res[name] = {}

        Currency = Pool().get('currency.currency')
        for line in lines:
            amount = line.on_change_with_moves_amount()
            if 'moves_amount' in names:
                res['moves_amount'][line.id] = amount
            if 'reconciled' in names:
                res['reconciled'][line.id] = (amount == line.amount)
            if 'company_amount' in names:
                amount = line.amount
                if line.statement_currency != line.company_currency:
                    amount = Currency.compute(line.statement_currency, amount,
                    line.company_currency)
                res['company_amount'][line.id] = amount
        return res

    def on_change_with_moves_amount(self):
        return sum([x.amount for x in self.bank_lines if x.amount])

    @classmethod
    @ModelView.button
    @Workflow.transition('confirmed')
    def confirm(cls, lines):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('posted')
    def post(cls, lines):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, lines):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('canceled')
    def cancel(cls, lines):
        Line = Pool().get('account.bank.reconciliation')

        unlink = []
        for line in lines:
            unlink += line.bank_lines
        Line.write(unlink, {
                'bank_statement_line': None,
                })
        cls.write(lines, {
            'state': 'canceled',
            })

    @classmethod
    def validate(cls, lines):
        for line in lines:
            line.check_amounts()

    def check_amounts(self):
        if self.state == 'posted' and self.company_amount != self.moves_amount:
            self.raise_user_error('different_amounts', {
                    'moves_amount': self.moves_amount,
                    'amount': self.company_amount,
                    'line': self.rec_name,
                    })

    def get_journal(self, name):
        return self.statement.journal.id

    @classmethod
    def search_journal(cls, name, clause):
        return [('statement.journal',) + clause[1:]]

    @classmethod
    def search(cls, args, offset=0, limit=None, order=None, count=False,
            query=False):
        """
        Override default search function so that if the user sorts by one field
        only, then 'sequence' is always added as a second sort field. This is
        specially important when the user sorts by date (the most usual) to
        ensure all moves from the same date are properly sorted.
        """
        if order is None:
            order = []
        order = list(order)
        if len(order) == 1:
            order.append(('sequence', order[0][1]))
        return super(StatementLine, cls).search(args, offset, limit, order,
            count, query)
