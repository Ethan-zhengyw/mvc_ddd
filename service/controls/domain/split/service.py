# -*- coding: utf-8 -*-

from typing import List, Optional

from common.util.log import get_logger
import service.controls.domain.split.factory as factory
from .aggr import BillPeriodAggr
from .entity import OriginalBill, LedgerBill, SplitRule, BillPeriod
from .val_obj import CompositeSplitPolicy, BillMatcher
from .iface import IBillPeriodSplitService

logger = get_logger('domain:split:service')


class BillPeriodSplitService(IBillPeriodSplitService):
    """ 计费周期分账服务

    根据分账规则，对计费周期内的原始账单进行分账，分账流程如下：

    1. 对于每一条原始账单，尝试与每一条分账规则进行匹配，根据匹配的分数高低，选择所要应用的分账规则
    2. 对于每一条原始账单，使用选中的分账规则进行分账，分账生成一条或多条总账账单
    3. 所有原始账单都处理完成后，汇总所有的总账账单，一次性覆盖计费周期的总账账单

    """
    @classmethod
    def split_original_bills_of_bill_period(cls, bill_period_id: int):
        aggr = BillPeriodAggr.get_by_id(bill_period_id)

        if not aggr:
            logger.warn(f'bill period of id {bill_period_id} not found, skipped.')
            return

        logger.info(f'start splitting original bills of bill period {aggr.bill_period.pretty_str}.')

        ledger_bills = []
        for original_bill in aggr.original_bills:
            split_rule = cls.__select_split_rule(aggr.split_rules, original_bill)
            if split_rule:
                for ledger_bill in cls.__split_original_bill_by_split_rule(original_bill, split_rule):
                    ledger_bills.append(ledger_bill)
            else:
                # 未与任何分账规则匹配，直接转为总账账单
                ledger_bill = factory.build_ledger_bill_by_original_bill(original_bill)
                ledger_bills.append(ledger_bill)

        logger.info(f'splitting original bills of bill period {aggr.bill_period.pretty_str} '
                    f'into {len(ledger_bills)} ledger bills, will be set.')

        cls.__overwrite_ledger_bills_of_bill_period(aggr, ledger_bills)

    @classmethod
    def __select_split_rule(cls, split_rules: List[SplitRule], original_bill: OriginalBill) -> Optional[SplitRule]:
        best_match: Optional[SplitRule] = None
        best_match_score = 0

        for split_rule in split_rules:
            bill_matcher = BillMatcher.get_by_split_rule(split_rule)

            if bill_matcher and bill_matcher.is_match(original_bill):
                match_score = bill_matcher.score
                if match_score > best_match_score:
                    best_match = split_rule
                    best_match_score = match_score

        if best_match:
            logger.info(f'original bill {original_bill.id} best match '
                        f'split rule {best_match.id} with score: {best_match_score}')

        return best_match

    @classmethod
    def __split_original_bill_by_split_rule(
            cls, original_bill: OriginalBill, split_rule: SplitRule) -> List[LedgerBill]:
        composite_split_policy: CompositeSplitPolicy = CompositeSplitPolicy.get_by_split_rule(split_rule)
        ledger_bills = composite_split_policy.split(original_bill)
        return ledger_bills

    @classmethod
    def __overwrite_ledger_bills_of_bill_period(cls, aggr: BillPeriodAggr, ledger_bills: List[LedgerBill]):
        aggr.set_ledger_bills(ledger_bills)


class LedgerBillSplitService:
    @classmethod
    def split_ledger_bill(cls, ledger_bill_id: int, ledger_bills: List[LedgerBill]):
        ledger_bill: LedgerBill = LedgerBill.query.filter_by(id=ledger_bill_id).first()

        if not ledger_bill:
            LedgerBill.raise_not_found(id=ledger_bill_id)

        aggr = BillPeriodAggr.get_by_id(ledger_bill.bill_period_id)

        if not aggr:
            BillPeriod.raise_not_found(id=ledger_bill.bill_period_id)

        aggr.split_ledger_bill(ledger_bill, ledger_bills)
