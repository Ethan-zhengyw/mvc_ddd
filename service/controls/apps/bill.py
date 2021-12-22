# -*- coding: utf-8 -*-

from typing import List
from service.models import *
from ..domain.split.service import LedgerBillSplitService


class LedgerBillApp:
    @classmethod
    def split(cls, ledger_bill_id: int, ledger_bills: List[LedgerBill]):
        """ 将一条总账账单拆分成多条

        使用领域内的LedgerBillSplitService服务实现，该服务使用以下等价操作实现总账账单拆分功能：
        1. 在计费周期内创建新的多条总账账单
        2. 删除原有总账账单
        """
        LedgerBillSplitService.split_ledger_bill(ledger_bill_id, ledger_bills)


class OriginalBillApp:
    @classmethod
    def get_split_results(cls, original_bill_id: int) -> List[LedgerBill]:
        return LedgerBill.query.filter_by(parent_id=original_bill_id).all()

    @classmethod
    def get_query_op_func_of_split_results(cls, original_bill_id: int):
        return lambda query: query\
            .filter_by(parent_id=original_bill_id).filter(Bill.bill_period_id.isnot(None))
