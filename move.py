#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.model import ModelView, fields
from trytond.pyson import Eval, PYSONEncoder
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateView, StateAction, Button
from trytond.transaction import Transaction
from decimal import Decimal

__metaclass__ = PoolMeta
__all__ = ['Line', 'Move', 'OpenBankReconcileLines',
    'OpenBankReconcileLinesStart']

_ZERO = Decimal('0.00')


class Move:
    __name__ = 'account.move'

    @classmethod
    def post(cls, moves):
        res = super(Move, cls).post(moves)
        BankMove = Pool().get('account.bank.reconciliation')
        bank_moves = []
        for move in moves:
            for line in move.lines:
                if line.account.bank_reconcile:
                    bank_move = {
                        'amount': line.debit - line.credit,
                        'move_line': line
                        }
                    bank_moves.append(bank_move)
        BankMove.create(bank_moves)
        return res

    @classmethod
    def draft(cls, moves):
        res = super(Move, cls).draft(moves)
        BankMove = Pool().get('account.bank.reconciliation')
        delete_bank_lines = []
        for move in moves:
            for line in move.lines:
                delete_bank_lines += [x for x in line.bank_lines]
        BankMove.delete(delete_bank_lines)
        return res


class Line:
    __name__ = 'account.move.line'

    bank_lines = fields.One2Many('account.bank.reconciliation', 'move_line',
        'Conciliation Lines')
    bank_amount = fields.Function(fields.Numeric('Bank Amount',
            digits=(16, Eval('currency_digits', 2)),
            on_change_with=['bank_lines'],
            depends=['currency_digits']),
            'get_bank_amounts')
    unreconciled_amount = fields.Function(fields.Numeric('Unreconciled Amount',
            digits=(16, Eval('currency_digits', 2)),
            on_change_with=['bank_lines'],
            depends=['currency_digits']),
            'get_bank_amounts')
    bank_reconciled = fields.Function(fields.Boolean('Bank Reconciled'),
            'get_bank_amounts', searcher='search_bank_reconciled')

    @classmethod
    def __setup__(cls):
        super(Line, cls).__setup__()
        cls._check_modify_exclude += ['bank_lines']
        cls._error_messages.update({
                'line_reconciled': ('Line "%(line)s" already reconciled with '
                'bank staement line "%(statment_line)s" with amont '
                '"%(amount)s". Please remove bank conciliation '
                'and try again.'),
                })

    @classmethod
    def search_bank_reconciled(cls, name, clause):
        pool = Pool()
        BankReconcile = pool.get('account.bank.reconciliation')
        cursor = Transaction().cursor
        cursor.execute(
            'SELECT id FROM ('
                'SELECT  id, '
                    'CASE WHEN bl.reconciled = (debit-credit) THEN  true '
                        ' ELSE false END as bank_reconciled'
                    ' FROM "'
                        + cls._table + '" LEFT JOIN '
                    '(SELECT move_line AS id , '
                        'SUM(amount) AS reconciled '
                    'FROM "' + BankReconcile._table + '" '
                    'WHERE '
                        'bank_statement_line IS NOT null '
                    'GROUP BY move_line ) AS bl USING(id) '
            ') as l WHERE ' +
                clause[0] + clause[1] + str(clause[2]))
        return [('id', 'in', [x[0] for x in cursor.fetchall()])]

    @classmethod
    def _get_origin(cls):
        return (super(Line, cls)._get_origin()
            + ['account.bank.statement.line'])

    @classmethod
    def delete(cls, lines):
        super(Line, cls).delete(lines)
        for line in lines:
            for bank_line in line.bank_lines:
                if bank_line.bank_statement_line:
                    bank_line.raise_user_error('line_reconciled', {
                        'line': line.rec_name,
                        'statement_line':
                            bank_line.bank_statement_line.rec_name,
                        'amount': bank_line.amount,
                        })

    def check_bank_lines(self):
        BankLine = Pool().get('account.bank.reconciliation')
        if self.bank_amount != self.debit - self.credit:
            bank_lines = [x for x in self.bank_lines
                if not x.bank_statement_line]
            BankLine.delete(bank_lines)
            bank_line = BankLine()
            bank_line.amount = self.bank_amount - (self.debit - self.credit)
            bank_line.move_line = self
            bank_line.save()

    @classmethod
    def get_bank_amounts(cls, lines,  names):
        res = {}
        for name in names:
            res[name] = {}

        for line in lines:
            for name in names:
                res[name][line.id] = 0
            for bank_line in line.bank_lines:
                if 'bank_amount' in names and bank_line.bank_statement_line:
                    res['bank_amount'][line.id] += bank_line.amount
                if 'unreconciled_amount' in names and \
                        not bank_line.bank_statement_line:
                    res['unreconciled_amount'][line.id] += bank_line.amount
            if 'bank_reconciled' in names:
                res['bank_reconciled'][line.id] = False
                if res['unreconciled_amount'][line.id] == _ZERO:
                    res['bank_reconciled'][line.id] = True
        return res


class OpenBankReconcileLinesStart(ModelView):
    'Open Bank Reconcile Lines (Start)'
    __name__ = 'account.move.open_bank_reconcile_lines.start'

    account = fields.Many2One('account.account', 'Account', required=True,
        domain=[('kind', '!=', 'view'), ('bank_reconcile', '=', True)])


class OpenBankReconcileLines(Wizard):
    'Open Bank Reconcile Lines'
    __name__ = 'account.move.open_bank_reconcile_lines'

    start = StateView('account.move.open_bank_reconcile_lines.start',
        'account_bank_statement.open_reconcile_bank_lines_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction(
        'account_bank_statement.act_move_line_bank_reconcile_form')

    def do_open_(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([
                ('account', '=', self.start.account.id)])
        return action, {}
