# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import List, Optional

from ex_dataclass import ex_dataclass, field, EXpack

import common.util.decimal as decimal

from .aggr import ReportAggr
from .entity import ReportBill


DataPointType = int
DPT_BILL_PERIOD = 0
DPT_BUSINESS = 1
DPT_SERVICE_TYPE = 2
DPT_TYPE_LEVEL_1 = 3


@ex_dataclass
class DataPoint(EXpack, metaclass=ABCMeta):
    total: decimal.Decimal = field(default_factory=decimal.Decimal)

    @property
    @abstractmethod
    def key(self):
        raise NotImplementedError

    @property
    def order_key(self):
        return self.key

    @staticmethod
    def loads_total(val: float):
        return decimal.Decimal(val or 0.0)

    def copy(self, **kwargs):
        new = type(self)(**self.asdict())
        for k, v in kwargs.items():
            setattr(new, k, v)
        return new


@ex_dataclass
class BillPeriodDataPoint(DataPoint):
    bill_period_timestamp: float = field(default=None)  # 用于排序
    bill_period: str = field(default=None)                # 格式：YYYY-MM

    @property
    def key(self):
        return self.bill_period

    @property
    def order_key(self):
        return self.bill_period_timestamp


@ex_dataclass
class BusinessDataPoint(DataPoint):
    business: str = field(default=None)

    @property
    def key(self):
        return self.business


@ex_dataclass
class ServiceTypeDataPoint(DataPoint):
    service_type: str = field(default=None)

    @property
    def key(self):
        return self.service_type


@ex_dataclass
class TypeLevel1DataPoint(DataPoint):
    type_level_1: str = field(default=None)

    @property
    def key(self):
        return self.type_level_1


@ex_dataclass
class ServiceTypeConsumptionTrend:
    service_type: str = field(default=None)
    data: List[BillPeriodDataPoint] = field(default_factory=list)


class ReportService:
    """ 基于给定的账单列表进行统计

    报表服务支持以下功能：

    0. 统计消费总额
    1. 统计消费趋势
    2. 按业务类型统计消费分布
    3. 按服务类型统计消费分布
    4. 按一级类型统计消费分布

    """
    @staticmethod
    def calc_total(report_bills: List[ReportBill]) -> float:
        total = decimal.Decimal('0.00')
        for report_bill in report_bills:
            if report_bill.actually_paid:
                # total += report_bill.actually_paid
                # 不知为何，测试用例运行时，actually_paid取得float
                # 实际运行，取得Decimal
                total += decimal.Decimal(report_bill.actually_paid)
        return total

    @classmethod
    def statistic_consumption_trend(cls, report_bills: List[ReportBill]) -> List[ServiceTypeConsumptionTrend]:
        """ 按服务类型统计消费趋势 """
        service_type_2_data_points = dict()

        # 准备数据点
        for report_bill in report_bills:

            if report_bill.service_type not in service_type_2_data_points:
                service_type_2_data_points[report_bill.service_type] = []

            service_type_2_data_points[report_bill.service_type].append(
                cls.__generate_data_point(report_bill, DPT_BILL_PERIOD))

        # 按计费周期合并数据点
        service_type_2_data_points_merged_by_period = dict()

        for service_type, data_points in service_type_2_data_points.items():
            if service_type not in service_type_2_data_points_merged_by_period:
                service_type_2_data_points_merged_by_period[service_type] = []

            service_type_2_data_points_merged_by_period[service_type] \
                = cls.__merge_data_points_by_key(data_points)

        # 按计费周期排序数据点
        for data_points in service_type_2_data_points_merged_by_period.values():
            cls.__sort_data_points(data_points)

        # 构造结果
        result: List[ServiceTypeConsumptionTrend] = []
        for service_type, data_points in service_type_2_data_points_merged_by_period.items():
            result.append(ServiceTypeConsumptionTrend(service_type=service_type, data=data_points))

        return result

    @classmethod
    def statistic_business_distribution(cls, report_bills: List[ReportBill]) -> List[BusinessDataPoint]:
        business_2_data_points = dict()

        # 生成数据点
        for report_bill in report_bills:
            if report_bill.business_modelx_code not in business_2_data_points:
                business_2_data_points[report_bill.business_modelx_code] = []
            data_point = cls.__generate_data_point(report_bill, DPT_BUSINESS)
            if data_point:
                business_2_data_points[report_bill.business_modelx_code].append(data_point)

        # 合并数据点
        merged_data_points = []
        for business, data_points in business_2_data_points.items():
            merged_data_points.append(BusinessDataPoint(**cls.__merge_data_points(data_points).asdict()))

        return merged_data_points

    @classmethod
    def statistic_service_type_distribution(cls, report_bills: List[ReportBill]) -> List[ServiceTypeDataPoint]:
        service_type_2_data_points = dict()

        # 生成数据点
        for report_bill in report_bills:
            if report_bill.service_type not in service_type_2_data_points:
                service_type_2_data_points[report_bill.service_type] = []
            data_point = cls.__generate_data_point(report_bill, DPT_SERVICE_TYPE)
            if data_point:
                service_type_2_data_points[report_bill.service_type].append(data_point)

        # 合并数据点
        merged_data_points = []
        for service_type, data_points in service_type_2_data_points.items():
            merged_data_points.append(ServiceTypeDataPoint(**cls.__merge_data_points(data_points).asdict()))

        return merged_data_points

    @classmethod
    def statistic_type_level_1_distribution(cls, report_bills: List[ReportBill]) -> List[TypeLevel1DataPoint]:
        type_level_1_2_data_points = dict()

        # 生成数据点
        for report_bill in report_bills:
            if report_bill.type_level_1 not in type_level_1_2_data_points:
                type_level_1_2_data_points[report_bill.type_level_1] = []
            data_point = cls.__generate_data_point(report_bill, DPT_TYPE_LEVEL_1)
            if data_point:
                type_level_1_2_data_points[report_bill.type_level_1].append(data_point)

        # 合并数据点
        merged_data_points = []
        for type_level_1, data_points in type_level_1_2_data_points.items():
            merged_data_points.append(TypeLevel1DataPoint(**cls.__merge_data_points(data_points).asdict()))

        return merged_data_points

    @staticmethod
    def __generate_data_point(report_bill: ReportBill, type_: DataPointType) -> Optional[DataPoint]:

        if type_ == DPT_BILL_PERIOD:

            report_aggr: ReportAggr = ReportAggr.get_by_bill_period_id(report_bill.bill_period_id)

            if report_aggr:
                bill_period = report_aggr.bill_period
                return BillPeriodDataPoint(
                    bill_period=bill_period.pretty_str,
                    bill_period_timestamp=bill_period.timestamp.timestamp(),
                    total=report_bill.actually_paid)
            else:
                return None

        elif type_ == DPT_BUSINESS:
            return BusinessDataPoint(
                business=report_bill.business_modelx_code,
                total=report_bill.actually_paid)

        elif type_ == DPT_SERVICE_TYPE:
            return ServiceTypeDataPoint(
                service_type=report_bill.service_type,
                total=report_bill.actually_paid)

        elif type_ == DPT_TYPE_LEVEL_1:
            return TypeLevel1DataPoint(
                type_level_1=report_bill.type_level_1,
                total=report_bill.actually_paid)

        else:
            # should not get here
            return None

    @classmethod
    def __merge_data_points_by_key(cls, data_points: List[DataPoint]) -> List[DataPoint]:
        """ 合并数据点列表

        按key对数据点进行合并

        当传入的数据点类型为计费周期数据点时输入输出示例如下：
            输入示例：
                2021-10 10
                2021-10 20
                2021-09 50

            输出示例：
                2021-10 30
                2021-09 50

        :param data_points: 待合并的数据点列表
        :return: 合并相同key的数据点后所得的数据点列表
        """
        key_2_data_points = dict()

        for data_point in data_points:
            if data_point.key not in key_2_data_points:
                key_2_data_points[data_point.key] = []
            key_2_data_points[data_point.key].append(data_point)

        merged_list = []
        for data_points in key_2_data_points.values():
            size = len(data_points)
            if size == 0:
                continue
            elif size == 1:
                merged_list.append(data_points[0])
            else:
                merged_list.append(cls.__merge_data_points(data_points))

        return merged_list

    @staticmethod
    def __merge_data_points(data_points: List[DataPoint]) -> DataPoint:
        """ 合并多个数据点

        待合并的多个数据点类型应相同，例如：均为计费周期数据点、均为服务类型数据点；
        待合并的相同类型的多个数据点的key应相同；
        合并后的数据点的total属性值为原数据点的total属性值之和。
        """
        first = data_points[0]

        merged_data_point = first.copy(total=decimal.Decimal('0.00'))

        for data_point in data_points:
            merged_data_point.total += data_point.total

        return merged_data_point

    @staticmethod
    def __sort_data_points(data_points: List[DataPoint]):
        data_points.sort(key=lambda data_point: data_point.order_key)
