# -*- coding: utf-8 -*-

from .meta import api as meta_api
from .user import api as user_api
from .bill_period import api as bill_period_api
from .split_rule import api as split_rule_api
from .original_bill import api as original_bill_api
from .ledger_bill import api as ledger_bill_api
from .report import api as report_api

__all__ = [
    "apis"
]


apis = [
    meta_api,
    user_api,
    bill_period_api,
    split_rule_api,
    original_bill_api,
    ledger_bill_api,
    report_api
]
