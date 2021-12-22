# -*- coding: utf-8 -*-

from typing import Optional, List
from .entity import LedgerBill
from .val_obj import BillMatcher, CompositeSplitPolicy, FixedValueSplitPolicy, ProportionalSplitPolicy
from ..meta.spec import MetaSpec, meta_spec


class BillMatcherSpec:
    def __init__(self, meta_spec: MetaSpec):
        self.__meta_spec = meta_spec

    def is_satisfied_by(self, bill_matcher: BillMatcher) -> (bool, Optional[str]):
        ok1, err1 = self.__is_provider_valid(bill_matcher.provider_name)
        ok2, err2 = self.__is_bill_subject_valid(bill_matcher.bill_subject_name)

        if ok1 and ok2:
            return True, None
        else:
            return False, "\n".join([str(e) for e in [err1, err2] if e is not None])

    def __is_provider_valid(self, provider: Optional[str]) -> (bool, Optional[str]):
        if provider is not None:
            return self.__meta_spec.is_provider_valid(provider)
        else:
            return True, None

    def __is_bill_subject_valid(self, bill_subject: Optional[str]) -> (bool, Optional[str]):
        if bill_subject is not None:
            return self.__meta_spec.is_bill_subject_valid(bill_subject)
        else:
            return True, None


class CompositeSplitPolicySpec:
    def __init__(self, meta_spec: MetaSpec):
        self.__meta_spec = meta_spec

    def is_satisfied_by(self, composite_split_policy: CompositeSplitPolicy) -> (bool, Optional[str]):
        ok1, err1 = self.__is_fixed_value_policies_valid(composite_split_policy.fixed_value_policies)
        ok2, err2 = True, None

        if len(composite_split_policy.proportional_policies) > 0:
            ok2, err2 = self.__is_proportional_policies_valid(composite_split_policy.proportional_policies)

        if ok1 and ok2:
            return True, None
        else:
            return False, '\n'.join([str(e) for e in [err1, err2] if e is not None])

    def __is_business_valid(self, business: str) -> (bool, Optional[str]):
        return self.__meta_spec.is_business_valid(business)

    def __is_fixed_value_policies_valid(
            self, fixed_value_policies: List[FixedValueSplitPolicy]) -> (bool, Optional[str]):
        oks, errs = [], []

        for p in fixed_value_policies:
            ok, err = self.__is_fixed_value_policy_valid(p)
            oks.append(ok)
            errs.append(err)

        if False not in oks:
            return True, None
        else:
            return False, '\n'.join([str(e) for e in errs if e is not None])

    def __is_proportional_policies_valid(
            self, proportional_policies: List[ProportionalSplitPolicy]) -> (bool, Optional[str]):
        oks, errs = [], []

        for p in proportional_policies:
            ok, err = self.__is_proportional_policy_valid(p)
            oks.append(ok)
            errs.append(err)

        # 比例之和需要为1
        sum_of_percent = sum([p.percent for p in proportional_policies])
        if sum_of_percent != 1:
            oks.append(False)
            errs.append(f'费用分摊的比例之和（{sum_of_percent}）不为1')

        if False not in oks:
            return True, None
        else:
            return False, '\n'.join([str(e) for e in errs if e is not None])

    def __is_fixed_value_policy_valid(
            self, fixed_value_policy: FixedValueSplitPolicy) -> (bool, Optional[str]):
        ok1, err1 = self.__is_business_valid(fixed_value_policy.business_modelx_code)
        ok2, err2 = self.__is_value_valid(fixed_value_policy.value)

        if ok1 and ok2:
            return True, None
        else:
            return False, '\n'.join([str(e) for e in [err1, err2] if e is not None])

    def __is_proportional_policy_valid(
            self, proportional_policy: ProportionalSplitPolicy) -> (bool, Optional[str]):
        ok1, err1 = self.__is_business_valid(proportional_policy.business_modelx_code)
        ok2, err2 = self.__is_percent_valid(proportional_policy.percent)

        if ok1 and ok2:
            return True, None
        else:
            return False, '\n'.join([str(e) for e in [err1, err2] if e is not None])

    @staticmethod
    def __is_percent_valid(percent: float) -> (bool, Optional[str]):
        if 0 <= percent <= 1:
            return True, None
        else:
            return False, f'费用分摊比例（{percent}）非法，合法范围：0.0~1.0'

    @staticmethod
    def __is_value_valid(value: float) -> (bool, Optional[str]):
        if value > 0:
            return True, None
        else:
            return False, f'固定值（{value}）非法，合法范围：> 0'


class LedgerBillSplitSpec:
    deviation = 0.0

    def __init__(self, ledger_bill: LedgerBill):
        self.ledger_bill = ledger_bill

    @classmethod
    def get_by_ledger_bill(cls, ledger_bill: LedgerBill) -> "LedgerBillSplitSpec":
        return cls(ledger_bill)

    def is_satisfied_by(self, ledger_bills: List[LedgerBill]) -> (bool, Optional[str]):
        sum_of_ledger_bills = sum([ledger_bill.actually_paid for ledger_bill in ledger_bills])
        if sum_of_ledger_bills - self.ledger_bill.actually_paid <= self.deviation:
            return True, None
        else:
            return False, f'账单实付金额（原账单实付：{self.ledger_bill.actually_paid}；' \
                          f'新账单实付合计：{sum_of_ledger_bills}）偏差超过允许范围（{self.deviation}）'


def bill_matcher_spec() -> BillMatcherSpec:
    return BillMatcherSpec(meta_spec())


def composite_split_policy_spec() -> CompositeSplitPolicySpec:
    return CompositeSplitPolicySpec(meta_spec())
