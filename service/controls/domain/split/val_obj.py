# -*- coding: utf-8 -*-

import json
from abc import ABCMeta, abstractmethod
from typing import List, Optional

from ex_dataclass import ex_dataclass, field, EXpack
from werkzeug.exceptions import InternalServerError

import common.static as const
import common.util.decimal as decimal
from common.util.log import get_logger
from . import factory
from .entity import SplitRule, OriginalBill, LedgerBill

logger = get_logger('domain:split:val_obj')


@ex_dataclass
class CommonConfig(EXpack):
    business: str = field(default_factory=str)
    percent: decimal.Decimal = field(default_factory=decimal.Decimal)
    value: decimal.Decimal = field(default_factory=decimal.Decimal)

    @staticmethod
    def loads_percent(percent: float):
        if isinstance(percent, decimal.Decimal):
            return percent
        elif isinstance(percent, str):
            return decimal.Decimal(str(percent)[:-1]) / decimal.Decimal('100.00')
        else:
            return decimal.Decimal(str(percent))

    @staticmethod
    def loads_value(value: float):
        if isinstance(value, decimal.Decimal):
            return value
        elif isinstance(value, str):
            return decimal.Decimal(str(value))
        else:
            return decimal.Decimal(str(value))

    @staticmethod
    def asdict_percent(percent: decimal.Decimal) -> str:
        return f'{percent * 100}%'


@ex_dataclass
class SubPolicy:
    type: const.SplitType = field(default_factory=str)
    configs: CommonConfig = field(default_factory=CommonConfig)


@ex_dataclass
class CompositePolicy(EXpack):
    type: const.SplitType = field(default=const.SPLIT_TYPE_COMP)
    configs: List[SubPolicy] = field(default_factory=list)


@ex_dataclass
class BillMatcher(EXpack):
    provider_name: Optional[str] = field(required=False, default=None)
    contract_id: Optional[str] = field(required=False, default=None)
    bill_subject_name: Optional[str] = field(required=False, default=None)
    service_type: Optional[str] = field(required=False, default=None)
    service_name: Optional[str] = field(required=False, default=None)
    service_details: Optional[str] = field(required=False, default=None)
    tag1: Optional[str] = field(required=False, default=None)
    tag2: Optional[str] = field(required=False, default=None)
    tag3: Optional[str] = field(required=False, default=None)
    tag4: Optional[str] = field(required=False, default=None)
    tag5: Optional[str] = field(required=False, default=None)

    @property
    def score(self) -> int:
        """ 返回该匹配器的分数

        分数即该匹配器中真正用于匹配的属性数
        真正用于匹配的属性是值非None的属性
        """
        num_of_not_none = 0
        for v in self.asdict().values():
            if v is not None:
                num_of_not_none += 1
        return num_of_not_none

    @classmethod
    def get_by_split_rule(cls, split_rule: SplitRule) -> Optional["BillMatcher"]:
        bm: Optional[BillMatcher] = None
        try:
            bm = BillMatcher(**split_rule.bill_matchers)
        except Exception as e:
            logger.error(f'build BillMatcher failed, bill_matchers: {json.dumps(split_rule.bill_matchers)}', exc=e)
        return bm

    def is_match(self, original_bill: OriginalBill) -> bool:
        oks = []

        for k in self.asdict().keys():
            oks.append(self.__is_attr_match(k, getattr(original_bill, k, None)))

        if False not in oks:
            return True
        else:
            return False

    def __is_attr_match(self, attr_name: Optional[str], attr_val: Optional[str]) -> bool:
        expect = getattr(self, attr_name, None)
        if expect is not None:
            return expect == attr_val
        else:
            return True


class ISplitPolicy(metaclass=ABCMeta):
    @abstractmethod
    def split(self, original_bill: OriginalBill) -> LedgerBill:
        raise NotImplementedError


class ProportionalSplitPolicy(ISplitPolicy):
    def __init__(self, business_modelx_code: str, percent: decimal.Decimal):
        self.business_modelx_code = business_modelx_code
        self.percent = percent
        self.base = None

    def split(self, original_bill: OriginalBill) -> LedgerBill:
        ledger_bill = factory.build_ledger_bill_by_original_bill(original_bill)
        ledger_bill.business_modelx_code = self.business_modelx_code
        ledger_bill.actually_paid = self.base * self.percent
        return ledger_bill

    def set_base(self, base: decimal.Decimal):
        self.base = base


class FixedValueSplitPolicy(ISplitPolicy):
    def __init__(self, business_modelx_code: str, value: decimal.Decimal):
        self.business_modelx_code = business_modelx_code
        self.value = value

    def split(self, original_bill: OriginalBill) -> LedgerBill:
        ledger_bill = factory.build_ledger_bill_by_original_bill(original_bill)
        ledger_bill.business_modelx_code = self.business_modelx_code
        ledger_bill.actually_paid = self.value
        return ledger_bill


class CompositeSplitPolicy(ISplitPolicy):
    def __init__(self,
                 fixed_value_policies: List[FixedValueSplitPolicy],
                 proportional_policies: List[ProportionalSplitPolicy]):
        self.__fixed_value_policies = fixed_value_policies
        self.__proportional_policies = proportional_policies

        self.__fixed_value_total: decimal.Decimal = sum([p.value for p in fixed_value_policies])

        # will be set when split start
        self.__original_bill: Optional[OriginalBill] = None

        # will be set empty when split start
        # ledger bill will be appended while splitting
        self.__ledger_bills: List[LedgerBill] = []

    @property
    def fixed_value_policies(self):
        return self.__fixed_value_policies

    @property
    def proportional_policies(self):
        return self.__proportional_policies

    @classmethod
    def get_by_split_rule(cls, split_rule: SplitRule) -> "CompositeSplitPolicy":
        split_policy = split_rule.split_policy

        try:
            cp = CompositePolicy(**split_policy)
        except Exception as e:
            logger.error(f'build CompositeSplitPolicy failed, split_policy: {json.dumps(split_policy)}', exc=e)
            raise InternalServerError(f'解析分账策略失败：{split_rule.split_policy}, details: {e}。')

        fixed_policies, prop_policies = [], []

        for p in cp.configs:
            if p.type == const.SPLIT_TYPE_FIXED:
                fixed_policies.append(FixedValueSplitPolicy(p.configs.business, p.configs.value))

            if p.type == const.SPLIT_TYPE_PROP:
                prop_policies.append(ProportionalSplitPolicy(p.configs.business, p.configs.percent))

        return cls(fixed_policies, prop_policies)

    def split(self, original_bill: OriginalBill) -> List[LedgerBill]:
        self.__pre_split(original_bill)
        self.__split_by_fixed_value_policies()
        self.__split_by_proportional_policies()
        return self.__ledger_bills

    def __pre_split(self, original_bill: OriginalBill):
        self.__original_bill = original_bill
        self.__ledger_bills = []

        # proportional_value_total = original_bill.actually_paid - self.__fixed_value_total
        # 不知为何，测试用例执行时，访问actually_paid得到的不是Decimal，而是float；
        # 实际运行没问题。
        proportional_value_total = decimal.Decimal(original_bill.actually_paid) - self.__fixed_value_total

        for p in self.__proportional_policies:
            p.set_base(proportional_value_total)

    def __split_by_fixed_value_policies(self):
        for p in self.__fixed_value_policies:
            ledger_bill = p.split(self.__original_bill)
            self.__ledger_bills.append(ledger_bill)

    def __split_by_proportional_policies(self):
        for p in self.__proportional_policies:
            ledger_bill = p.split(self.__original_bill)
            self.__ledger_bills.append(ledger_bill)
