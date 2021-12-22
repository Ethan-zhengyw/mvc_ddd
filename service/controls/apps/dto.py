# -*- coding: utf-8 -*-

from typing import List, Dict
from werkzeug.exceptions import BadRequest

from ex_dataclass import ex_dataclass, field, EXpack

from ..domain.split.val_obj import BillMatcher, CompositePolicy, SubPolicy, CommonConfig
from ..domain.split.entity import SplitRule
from ..domain.report.entity import ReportBill
from ..domain.report.service import \
    ServiceTypeConsumptionTrend, BusinessDataPoint, ServiceTypeDataPoint, TypeLevel1DataPoint

import common.static as const
import common.util.decimal as decimal


@ex_dataclass
class ReportOverview:
    total: float = field(required=True)
    bills: List[ReportBill] = field(required=True)


@ex_dataclass
class ReportPlots:
    consumption_trend: List[ServiceTypeConsumptionTrend] = field(required=True)
    business_distribution: List[BusinessDataPoint] = field(required=True)
    service_type_distribution: List[ServiceTypeDataPoint] = field(required=True)
    type_level_1_distribution: List[TypeLevel1DataPoint] = field(required=True)


@ex_dataclass
class ReportDetails(EXpack):
    overview: ReportOverview = field(required=True)
    plots: ReportPlots = field(required=True)

    def asdict(self) -> Dict:
        res = super().asdict()
        bill_dict_list = []
        for bill in self.overview.bills:
            bill_dict_list.append(bill.to_dict(excludes=['type', 'parent_id']))
        res['overview']['bills'] = bill_dict_list
        return res


@ex_dataclass
class SimpleSplitRule(EXpack):
    contract_id: str = field(default=None)
    provider_name: str = field(default=None)
    bill_subject_name: str = field(default=None)
    service_type: str = field(default=None)
    service_name: str = field(default=None)
    service_details: str = field(default=None)
    desc: str = field(default=None)
    tag1: str = field(default=None)
    tag2: str = field(default=None)
    tag3: str = field(default=None)
    tag4: str = field(default=None)
    tag5: str = field(default=None)
    split_policy: str = field(default=None)

    def to_split_rule(self) -> SplitRule:
        rule = SplitRule.create()
        rule.bill_matchers = self.__build_bill_matcher().asdict()
        rule.split_policy = self.__build_split_policy().asdict()
        rule.desc = self.desc
        return rule

    def __build_bill_matcher(self) -> BillMatcher:
        dict_data = self.asdict()
        dict_data.pop('split_policy')
        bm = BillMatcher(**dict((k, v) for (k, v) in dict_data.items() if (v is not None and v != '')))
        return bm

    def __build_split_policy(self) -> CompositePolicy:
        """ 按约定的格式解析split_policy，返回CompositePolicy

        1. 每一行表示一条分摊策略
        2. 条目中，若数值字符串不包含小数点，则表示策略类型为固定数值；否则表示按比例

        业务1: 200000
        业务2: 0.8
        业务3: 0.1
        运维:   0.1

        """
        text = self.split_policy.strip()

        policies: List[SubPolicy] = []

        for line in text.split('\n'):
            items = line.split(':')

            if len(items) != 2:
                raise BadRequest(f'解析分摊策略失败，原因：行{line}不符合约定的格式（e.g. "业务1: 200000", "业务2: 0.8"）。')

            business = items[0].strip()
            value_or_percent = items[1].strip()

            policy = self.__build_sub_policy_or_raise(value_or_percent, business)

            policies.append(policy)

        cp = CompositePolicy(type=const.SPLIT_TYPE_COMP, configs=policies)

        return cp

    @classmethod
    def __build_sub_policy_or_raise(cls, sub_policy_str: str, business: str) -> SubPolicy:
        """ 根据给定的字符串生成SubPolicy对象

        :param sub_policy_str: 可能是以下三种情况

            1. 固定值类型子策略：xxxxx.xx
            2. 按比例类型子策略：xx.xx%
            3. 都不是
        """
        value_or_percent = sub_policy_str

        policy = SubPolicy(configs=CommonConfig(business=business))

        if cls.__is_fixed_value_str(value_or_percent):

            decimal_value = cls.__convert_fixed_value_str_2_decimal_or_raise(value_or_percent)
            policy.type = const.SPLIT_TYPE_FIXED
            policy.configs.value = decimal_value

        elif cls.__is_percent_str(value_or_percent):

            decimal_value = cls.__convert_percent_str_2_decimal_or_raise(value_or_percent)
            policy.type = const.SPLIT_TYPE_PROP
            policy.configs.percent = decimal_value

        else:

            cls.__raise_decode_sub_policy_failed(sub_policy_str)

        return policy

    @classmethod
    def __is_fixed_value_str(cls, value_or_percent_str: str) -> bool:
        return '%' not in value_or_percent_str

    @classmethod
    def __is_percent_str(cls, value_or_percent_str: str) -> bool:
        return '%' in value_or_percent_str

    @classmethod
    def __convert_fixed_value_str_2_decimal_or_raise(cls, fixed_value_str: str) -> decimal.Decimal:
        try:
            return decimal.Decimal(fixed_value_str)
        except decimal.DecimalException:
            cls.__raise_decode_sub_policy_failed(fixed_value_str)

    @classmethod
    def __convert_percent_str_2_decimal_or_raise(cls, percent_str: str) -> decimal.Decimal:
        try:
            return decimal.Decimal(percent_str[:-1]) / decimal.Decimal('100.00')
        except decimal.DecimalException:
            cls.__raise_decode_sub_policy_failed(percent_str)

    @classmethod
    def __raise_decode_sub_policy_failed(cls, sub_policy_str: str):
        raise BadRequest(f'解析分摊策略失败，原因：解析{sub_policy_str}固定数值或比例失败。')
