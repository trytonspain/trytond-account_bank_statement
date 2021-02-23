# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from datetime import datetime
import pytz
import csv
from io import StringIO
from decimal import Decimal
from trytond.model import Workflow, ModelView, ModelSQL, fields, \
    sequence_ordered
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pool import Pool
from trytond.rpc import RPC
from trytond.pyson import Eval, Not, Equal, If
from trytond.transaction import Transaction
from trytond import backend
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['Statement', 'StatementLine', 'ImportStart', 'Import']

_STATES = {'readonly': Eval('state') != 'draft'}
_DEPENDS = ['state']
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
    company = fields.Many2One('company.company', 'Company', required=True,
        states=_STATES, depends=['state'], select=True)
    date = fields.DateTime('Date', required=True, states=_STATES,
        depends=['state'], help='Created date bank statement')
    start_date = fields.Date('Start Date', required=True,
        states=_STATES, depends=['state'], help='Start date bank statement')
    end_date = fields.Date('End Date', required=True,
        states=_STATES, depends=['state'], help='End date bank statement')
    start_balance = fields.Numeric('Start Balance', required=True,
        digits=(16, Eval('currency_digits', 2)),
        states=_STATES, depends=['state', 'currency_digits'])
    end_balance = fields.Numeric('End Balance', required=True,
        digits=(16, Eval('currency_digits', 2)),
        states=_STATES, depends=['state', 'currency_digits'])
    journal = fields.Many2One('account.bank.statement.journal', 'Journal',
        required=True, domain=[
            ('company', '=', Eval('company')),
            ],
        states=_STATES, depends=['state', 'company'])
    lines = fields.One2Many('account.bank.statement.line', 'statement',
        'Lines', domain=[
            ('company', '=', Eval('company')),
            ], depends=['company'])
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
        'on_change_with_currency_digits')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('canceled', 'Canceled'),
            ], 'State', required=True, readonly=True)

    @classmethod
    def __setup__(cls):
        super(Statement, cls).__setup__()
        cls._order.insert(0, ('date', 'DESC'))
        cls._transitions |= set((
                ('draft', 'confirmed'),
                ('confirmed', 'canceled'),
                ('canceled', 'draft'),
                ('draft', 'canceled'),
                ))
        cls._buttons.update({
                'confirm': {
                    'invisible': ~Eval('state').in_(['draft']),
                    'icon': 'tryton-forward',
                    },
                'draft': {
                    'invisible': ~Eval('state').in_(['canceled']),
                    'icon': If(Eval('state') == 'canceled',
                        'tryton-undo',
                        'tryton-back'),
                    'depends': ['state'],
                    },
                'cancel': {
                    'invisible': Eval('state').in_(['canceled']),
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
        return datetime.now()

    @staticmethod
    def default_start_date():
        return Pool().get('ir.date').today()

    @staticmethod
    def default_end_date():
        return Pool().get('ir.date').today()

    @staticmethod
    def default_start_balance():
        return Decimal('0.0')

    @fields.depends('journal')
    def on_change_with_currency_digits(self, name=None):
        if self.journal:
            return self.journal.currency.digits
        return 2

    @staticmethod
    def default_end_balance():
        return Decimal('0.0')

    def get_rec_name(self, name):
        return '%s' % (self.date.strftime("%Y-%m-%d"))

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
                if line.state not in ('draft', 'canceled'):
                    raise UserError(gettext(
                        'account_bank_statement.cannot_cancel_statement_line',
                            line=line.rec_name,
                            state=line.state))
            lines += statement.lines
        StatementLine.cancel(lines)

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, statements):
        StatementLine = Pool().get('account.bank.statement.line')
        lines = []
        for statement in statements:
            lines += statement.lines
        StatementLine.cancel(lines)

    @classmethod
    def delete(cls, statements):
        for statement in statements:
            if statement.lines:
                raise UserError(gettext('account_bank_statement.cannot_delete',
                    statement=statement.rec_name))
        super(Statement, cls).delete(statements)


class StatementLine(sequence_ordered(), Workflow, ModelSQL, ModelView):
    'Bank Statement Line'
    __name__ = 'account.bank.statement.line'
    _rec_name = 'description'

    statement = fields.Many2One('account.bank.statement', 'Statement',
        required=True, domain=[
            ('company', '=', Eval('company')),
            ],
        states=CONFIRMED_STATES, depends=CONFIRMED_DEPENDS + ['company'])
    company = fields.Many2One('company.company', 'Company', required=True,
        select=True, states=CONFIRMED_STATES)
    date = fields.Function(fields.DateTime('Date', required=True), 'get_date_utc',
        searcher='search_date_utc', setter='set_date_utc')
    date_utc = fields.DateTime('Date UTC', states=CONFIRMED_STATES)
    description = fields.Char('Description', required=True,
        states=CONFIRMED_STATES)
    notes = fields.Char('Notes', states=POSTED_STATES)
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
    account = fields.Function(fields.Many2One('account.account',
            'Account'), 'get_account')
    moves_amount = fields.Function(fields.Numeric('Moves Amount',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']),
            'on_change_with_moves_amount')
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
            depends=['company_currency_digits']),
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
        cls._order.insert(0, ('date_utc', 'ASC'))
        cls._transitions |= set((
                ('draft', 'confirmed'),
                ('confirmed', 'posted'),
                ('canceled', 'draft'),
                ('draft', 'canceled'),
                ('confirmed', 'canceled'),
                ('posted', 'canceled'),
                ))
        cls._buttons.update({
                'confirm': {
                    'invisible': ~Eval('state').in_(['draft']),
                    'icon': 'tryton-forward',
                    },
                'post': {
                    'invisible': Eval('state').in_([
                            'draft', 'canceled', 'posted']),
                    'icon': 'tryton-ok',
                    },
                'cancel': {
                    'invisible': Eval('state').in_(['canceled']),
                    },
                'draft': {
                    'invisible': ~Eval('state').in_(['canceled']),
                    'icon': If(Eval('state') == 'canceled',
                        'tryton-undo',
                        'tryton-back'),
                    'depends': ['state'],
                    },
                })
        cls.__rpc__.update({
                'post': RPC(
                    readonly=False, instantiate=0, fresh_session=True),
                })

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')

        table = TableHandler(cls, module_name)

        # Migration: rename date into date_utc
        if (table.column_exist('date')
                and not table.column_exist('date_utc')):
            table.not_null_action('date', 'remove')
            table.column_rename('date', 'date_utc')

        super(StatementLine, cls).__register__(module_name)

    @classmethod
    def get_date_utc(cls, lines, names):
        # get date + UTC
        result = {}
        for name in names:
            result[name] = dict((l.id, None) for l in lines)

        for line in lines:
            for name in names:
                line_date = getattr(line, name + '_utc')
                if (line_date and line.statement
                        and line.statement.company.timezone):
                    timezone = pytz.timezone(line.statement.company.timezone)
                    date = timezone.localize(line_date)
                    line_date += date.utcoffset()
                result[name][line.id] = line_date
        return result

    @classmethod
    def search_date_utc(cls, name, clause):
        return [(name + '_utc',) + tuple(clause[1:])]

    @classmethod
    def set_date_utc(cls, lines, name, value):
        if not value:
            return

        # set date to UTC
        timezone = None
        for line in lines:
            if (line.statement and line.statement.company
                    and line.statement.company.timezone):
                timezone = line.statement.company.timezone
                break
        if timezone and value:
            timezone = pytz.timezone(timezone)
            date = timezone.localize(value)
            value -= date.utcoffset()

        cls.write(lines, {
            name + '_utc': value,
            })

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_date():
        return datetime.now()

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_currency_digits():
        return 2

    @staticmethod
    def default_company_currency_digits():
        return 2

    def get_currency_digits(self, name):
        return self.statement_currency.digits

    def get_company_currency_digits(self, name):
        return self.company_currency.digits

    def get_statement_currency(self, name):
        return self.statement.journal.currency.id

    def get_company_currency(self, name):
        return self.statement.company.currency.id

    def get_account(self, name):
        account = self.statement.journal.account
        return account and account.id

    @classmethod
    def get_accounting_vals(cls, lines, names):
        res = {}
        line_ids = [l.id for l in lines]
        for name in names:
            value = Decimal('0.0')
            res[name] = {}.fromkeys(line_ids, value)

        Currency = Pool().get('currency.currency')
        for line in lines:
            amount = line.company_currency.round(line.moves_amount)
            company_amount = line.company_currency.round(line.amount)
            if line.statement_currency != line.company_currency:
                with Transaction().set_context(date=line.date.date()):
                    company_amount = Currency.compute(
                        line.statement_currency, company_amount,
                        line.company_currency)
            if 'company_amount' in names:
                res['company_amount'][line.id] = company_amount
        return res

    @fields.depends('company_currency', 'date')
    def on_change_with_moves_amount(self, name=None):
        if hasattr(self, 'statement') and self.statement:
            amount = sum([x.amount for x in self.statement.lines if x.amount],
                Decimal('0.0'))
        else:
            amount = Decimal('0.0')
        if self.company_currency:
            amount = self.company_currency.round(amount)
        return amount

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

        with Transaction().set_context(from_account_bank_statement_line=True):
            cls.write(lines, {
                'state': 'canceled',
                })


    def get_journal(self, name):
        return self.statement.journal.id

    @classmethod
    def search_journal(cls, name, clause):
        return [('statement.journal',) + tuple(clause[1:])]

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
            order = cls._order
        order = list(order)
        if len(order) == 1:
            order.append(('sequence', order[0][1]))
        return super(StatementLine, cls).search(args, offset, limit, order,
            count, query)

    @classmethod
    def copy(cls, lines, default=None):
        if default is None:
            default = {}
        if 'bank_lines' not in default:
            default['bank_lines'] = None
        return super(StatementLine, cls).copy(lines, default)

    @classmethod
    def delete(cls, lines):
        for line in lines:
            if line.state not in ('draft', 'canceled'):
                raise UserError(gettext(
                    'account_bank_statement.cannot_delete_statement_line',
                        line=line.rec_name))
        super(StatementLine, cls).delete(lines)


class ImportStart(ModelView):
    'Import Start'
    __name__ = 'account.bank.statement.import.start'
    import_file = fields.Binary('File', required=True)
    type = fields.Selection([
            ('csv', 'CSV (date, description, amount)'),
            ], 'Type', required=True)
    attachment = fields.Boolean('Attach file after import')
    confirm = fields.Boolean('Confirm',
        help='Confirm Bank Statement after import.')

    @classmethod
    def default_attachment(cls):
        return True

    @classmethod
    def default_confirm(cls):
        return True


class Import(Wizard):
    'Import'
    __name__ = 'account.bank.statement.import'
    start = StateView('account.bank.statement.import.start',
        'account_bank_statement.import_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Import File', 'import_file', 'tryton-ok', default=True),
            ])
    import_file = StateTransition()

    def transition_import_file(self):
        pool = Pool()
        BankStatement = pool.get('account.bank.statement')
        Attachment = pool.get('ir.attachment')

        statement = BankStatement(Transaction().context['active_id'])
        if statement.lines:
            raise UserError(gettext('account_bank_statement_already_has_lines'))

        self.process(statement)

        if self.start.confirm:
            BankStatement.confirm([statement])

        if self.start.attachment:
            attach = Attachment(
                name=datetime.now().strftime("%y/%m/%d %H:%M:%S"),
                type='data',
                data=self.start.import_file,
                resource=str(statement))
            attach.save()
        return 'end'

    def process(self, statement):
        if self.start.type != 'csv':
            return
        BankStatementLine = Pool().get('account.bank.statement.line')

        csv_file = StringIO(self.start.import_file.decode('utf-8'))
        try:
            reader = csv.reader(csv_file)
        except csv.Error as e:
            raise UserError(gettext('account_bank_statement.format_error',
                error=str(e)))

        count = 0
        lines = []
        for record in reader:
            count += 1
            if len(record) < 3:
                raise UserError(gettext(
                    'account_bank_statement.missing_columns',
                    columns=str(count)))
            line = BankStatementLine()
            line.statement = statement
            line.date = self.string_to_date(record[0])
            line.description = record[1] or ''
            line.amount = self.string_to_number(record[2])
            lines.append(line)
        BankStatementLine.save(lines)

    def string_to_date(self, text, patterns=('%d/%m/%Y', '%Y-%m-%d')):
        for pattern in patterns:
            try:
                return datetime.strptime(text, pattern)
            except ValueError:
                continue
        raise UserError(gettext('account_bank_statement.invalid_date',
            date=text))

    def string_to_number(self, text, decimal_separator='.',
            thousands_separator=','):
        text = text.replace(thousands_separator, '')
        if decimal_separator != '.':
            text = text.replace(decimal_separator, '.')
        try:
            return Decimal(text)
        except ValueError:
            raise UserError(gettext('account_bank_statement.invalid_number',
                number=text))
