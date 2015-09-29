================================
Account Bank Statement Scenario
================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
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

    >>> Currency = Model.get('currency.currency')
    >>> CurrencyRate = Model.get('currency.currency.rate')
    >>> currencies = Currency.find([('code', '=', 'USD')])
    >>> if not currencies:
    ...     dollar = Currency(name='US Dollar', symbol=u'$', code='USD',
    ...         rounding=Decimal('0.01'), mon_grouping='[]',
    ...         mon_decimal_point='.')
    ...     dollar.save()
    ...     CurrencyRate(date=today + relativedelta(month=1, day=1),
    ...         rate=Decimal('1.25'), currency=dollar).save()
    ... else:
    ...     dollar, = currencies
    >>> Company = Model.get('company.company')
    >>> Party = Model.get('party.party')
    >>> company_config = Wizard('company.company.config')
    >>> company_config.execute('company')
    >>> company = company_config.form
    >>> party = Party(name='Dunder Mifflin')
    >>> party.save()
    >>> company.party = party
    >>> company.currency = dollar
    >>> company_config.execute('add')
    >>> company, = Company.find([])

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> FiscalYear = Model.get('account.fiscalyear')
    >>> Sequence = Model.get('ir.sequence')
    >>> SequenceStrict = Model.get('ir.sequence.strict')
    >>> fiscalyear = FiscalYear(name=str(today.year))
    >>> fiscalyear.start_date = today + relativedelta(month=1, day=1)
    >>> fiscalyear.end_date = today + relativedelta(month=12, day=31)
    >>> fiscalyear.company = company
    >>> post_move_seq = Sequence(name=str(today.year), code='account.move',
    ...     company=company)
    >>> post_move_seq.save()
    >>> fiscalyear.post_move_sequence = post_move_seq
    >>> fiscalyear.save()
    >>> FiscalYear.create_period([fiscalyear.id], config.context)

Create chart of accounts::

    >>> AccountTemplate = Model.get('account.account.template')
    >>> Account = Model.get('account.account')
    >>> account_template, = AccountTemplate.find([('parent', '=', None)])
    >>> create_chart = Wizard('account.create_chart')
    >>> create_chart.execute('account')
    >>> create_chart.form.account_template = account_template
    >>> create_chart.form.company = company
    >>> create_chart.execute('create_account')
    >>> receivable, = Account.find([
    ...         ('kind', '=', 'receivable'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> payable, = Account.find([
    ...         ('kind', '=', 'payable'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> revenue, = Account.find([
    ...         ('kind', '=', 'revenue'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> expense, = Account.find([
    ...         ('kind', '=', 'expense'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> account_tax, = Account.find([
    ...         ('kind', '=', 'other'),
    ...         ('company', '=', company.id),
    ...         ('name', '=', 'Main Tax'),
    ...         ])
    >>> cash, = Account.find([
    ...         ('kind', '=', 'other'),
    ...         ('company', '=', company.id),
    ...         ('name', '=', 'Main Cash'),
    ...         ])
    >>> cash.bank_reconcile = True
    >>> cash.save()
    >>> create_chart.form.account_receivable = receivable
    >>> create_chart.form.account_payable = payable
    >>> create_chart.execute('create_properties')

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

Create Statement Journal::

    >>> StatementJournal = Model.get('account.bank.statement.journal')
    >>> statement_journal_dollar = StatementJournal(name='Test',
    ...     journal=account_journal, currency=dollar)
    >>> statement_journal_dollar.save()

Create Bank Move::

    >>> period = fiscalyear.periods[0]
    >>> Move = Model.get('account.move')
    >>> move = Move()
    >>> move.period = period
    >>> move.journal = account_journal
    >>> move.date = period.start_date
    >>> line = move.lines.new()
    >>> line.account = cash
    >>> line.credit = Decimal('80.0')
    >>> line2 = move.lines.new()
    >>> line2.account = receivable
    >>> line2.debit = Decimal('80.0')
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
    >>> statement_line.amount = Decimal('80.0')
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
