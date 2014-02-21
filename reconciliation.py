#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval
from trytond.const import OPERATORS

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
    def write(cls, lines, vals):
        res = super(AccountBankReconciliation, cls).write(lines, vals)
        move_lines = set([x.move_line for x in lines])
        for move_line in move_lines:
            move_line.check_bank_lines()
        return res

    @classmethod
    def delete(cls, lines):
        unallowed = [x for x in lines if x.bank_statement_line]
        if unallowed:
            line, = unallowed
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
    def search_domain(cls, domain, active_test=True):
        def convert_domain(domain):
            'Replace missing Reconciliation field by the MoveLine one'
            if not domain:
                return []
            operator = 'AND'
            if isinstance(domain[0], basestring):
                operator = domain[0]
                domain = domain[1:]
            result = [operator]
            for arg in domain:
                if (isinstance(arg, (list, tuple))
                        and len(arg) > 2
                        and isinstance(arg[1], basestring)
                        and arg[1] in OPERATORS):
                    # clause
                    field = arg[0].split('.', 1)[0]
                    if not getattr(cls, field, None):
                        field = 'move_line.' + arg[0]
                    result.append((field,) + tuple(arg[1:]))
                elif isinstance(arg, list):
                    # sub-domain
                    result.append(convert_domain(arg))
                else:
                    result.append(arg)
            return result
        return super(AccountBankReconciliation, cls).search_domain(
            convert_domain(domain), active_test=active_test)

    def get_currency_digits(self, name):
        return self.account.company.currency.digits

    @staticmethod
    def default_state():
        return 'confirmed'
