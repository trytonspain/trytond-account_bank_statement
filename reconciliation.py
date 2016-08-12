# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.const import OPERATORS
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = ['AccountBankReconciliation']


class AccountBankReconciliation(ModelView, ModelSQL):
    'Account Bank Reconciliation'
    __name__ = 'account.bank.reconciliation'

    amount = fields.Numeric('Amount', digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'], required=True)
    currency_digits = fields.Function(fields.Integer('currency digits'),
            'get_currency_digits')
    move_line = fields.Many2One('account.move.line', 'Move Line',
        required=True, readonly=True)
    bank_statement_line = fields.Many2One('account.bank.statement.line',
        'Bank Statement Line')

    @classmethod
    def __setup__(cls):
        super(AccountBankReconciliation, cls).__setup__()
        cls._error_messages.update({
                'delete_reconciled': ('Bank Reconciliation Line with amount '
                    '"%(amount)s" in statement_line "%(statement_line)s" '
                    'cannot be deleted')
                })

    @classmethod
    def write(cls, *args):
        super(AccountBankReconciliation, cls).write(*args)
        actions = iter(args)
        for lines, _ in zip(actions, actions):
            move_lines = set([x.move_line for x in lines])
            for move_line in move_lines:
                move_line.check_bank_lines()

    @classmethod
    def delete(cls, lines):
        if not Transaction().context.get('from_account_bank_statement_line'):
            unallowed = [x for x in lines if x.bank_statement_line]
            if unallowed:
                line = unallowed[0]
                line.raise_user_error('delete_reconciled', {
                    'amount': line.amount,
                    'statement_line': line.bank_statement_line.rec_name
                    })
        super(AccountBankReconciliation, cls).delete(lines)

    def __getattr__(self, name):
        try:
            return super(AccountBankReconciliation, self).__getattr__(name)
        except AttributeError:
            pass
        return getattr(self.move_line, name)

    @classmethod
    def search_domain(cls, domain, active_test=True, tables=None):
        def is_leaf(expression):
            return (isinstance(expression, (list, tuple))
                and len(expression) > 2
                and isinstance(expression[1], basestring)
                and expression[1] in OPERATORS)  # TODO remove OPERATORS test

        def convert_domain(domain):
            'Replace missing product field by the MoveLine one'
            if is_leaf(domain):
                field = domain[0].split('.', 1)[0]
                if not getattr(cls, field, None):
                    field = 'move_line.' + domain[0]
                    return (field,) + tuple(domain[1:])
                else:
                    return domain
            elif domain in ['OR', 'AND']:
                return domain
            else:
                return [convert_domain(d) for d in domain]
        return super(AccountBankReconciliation, cls).search_domain(
            convert_domain(domain), active_test=active_test, tables=tables)

    def get_currency_digits(self, name):
        return self.account.company.currency.digits
