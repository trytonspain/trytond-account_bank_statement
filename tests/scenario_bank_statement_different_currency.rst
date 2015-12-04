=======================================================
Account Bank Statement With Different Currency Scenario
=======================================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from.trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()
    >>> now = datetime.datetime.now()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install account_bank_statement::

    >>> Module = Model.get('ir.module')
    >>> account_bank_module, = Module.find(
    ...     [('name', '=', 'account_bank_statement')])
    >>> Module.install([account_bank_module.id], config.context)
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> cash = accounts['cash']

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party')
    >>> party.save()

Create Journal::

    >>> sequence = Sequence(name='Bank', code='account.journal',
    ...     company=company)
    >>> sequence.save()
    >>> AccountJournal = Model.get('account.journal')
    >>> account_journal = AccountJournal(name='Statement',
    ...     type='cash',
    ...     credit_account=cash,
    ...     debit_account=cash,
    ...     sequence=sequence)
    >>> account_journal.save()

Create Dollar Statement Journal::

    >>> StatementJournal = Model.get('account.bank.statement.journal')
    >>> statement_journal_dollar = StatementJournal(name='Test',
    ...     journal=account_journal, currency=dollar)
    >>> statement_journal_dollar.save()

Create Euro Statement Journal::

    >>> statement_journal_euro = StatementJournal(name='Test',
    ...     journal=account_journal, currency=euro)
    >>> statement_journal_euro.save()

Create Bank Move::

    >>> period = fiscalyear.periods[0]
    >>> Move = Model.get('account.move')
    >>> move = Move()
    >>> move.period = period
    >>> move.journal = account_journal
    >>> move.date = period.start_date
    >>> line = move.lines.new()
    >>> line.account = cash
    >>> line.debit = Decimal('80.0')
    >>> line2 = move.lines.new()
    >>> line2.account = receivable
    >>> line2.credit = Decimal('80.0')
    >>> line2.party = party
    >>> move.save()
    >>> Move.post([move.id], config.context)
    >>> move.reload()
    >>> move.state
    u'posted'

Create Bank Statement With Different Curreny::

    >>> BankStatement = Model.get('account.bank.statement')
    >>> statement = BankStatement(journal=statement_journal_dollar, date=now)

Create Bank Statement Lines::

    >>> StatementLine = Model.get('account.bank.statement.line')
    >>> statement_line = StatementLine()
    >>> statement.lines.append(statement_line)
    >>> statement_line.date = now
    >>> statement_line.description = 'Statement Line'
    >>> statement_line.amount = Decimal('80.0') * Decimal('1.25')
    >>> statement_line.party = party
    >>> statement.save()
    >>> statement.reload()
    >>> BankStatement.confirm([statement.id], config.context)
    >>> statement.reload()
    >>> statement.state
    u'confirmed'
    >>> statement_line = StatementLine(1)
    >>> statement_line.state
    u'confirmed'

Select statement move to reconcile statement line::

    >>> MoveLine = Model.get('account.move.line')
    >>> line = MoveLine(1)
    >>> BankLine = Model.get('account.bank.reconciliation')
    >>> bank_line, = BankLine.find([])
    >>> bank_line.amount = Decimal('80.0')
    >>> bank_line.bank_statement_line = statement_line
    >>> bank_line.save()
    >>> bank_line.reload()
    >>> statement_line.save()
    >>> statement_line.reload()
    >>> statement_line.moves_amount == Decimal('80.0')
    True
    >>> statement_line.company_amount == Decimal('80.0')
    True
    >>> statement_line.moves_amount == statement_line.company_amount
    True

Post line::

    >>> StatementLine.post([statement_line.id], config.context)
    >>> statement_line.reload()
    >>> statement_line.state
    u'posted'

Cancel line::

    >>> StatementLine.cancel([statement_line.id], config.context)
    >>> statement_line.reload()
    >>> statement_line.state
    u'canceled'
    >>> statement_line.bank_lines
    []
