# -*- coding: utf-8 -*-

from .entity import OriginalBill, LedgerBill
import common.static as const


def build_ledger_bill_by_original_bill(original_bill: OriginalBill) -> LedgerBill:

    kwargs = original_bill.to_dict()

    for key in ['id', 'create_time', 'update_time']:
        kwargs.pop(key)

    ledger_bill: LedgerBill = LedgerBill.create(**kwargs)

    ledger_bill.bill_period_id = original_bill.bill_period_id
    ledger_bill.type = const.BILL_TYPE_LEDGER
    ledger_bill.parent_id = original_bill.id

    return ledger_bill
