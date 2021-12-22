# -*- coding: utf-8 -*-

import os
from typing import Any, IO

from sqlalchemy import and_

from common.util.excel import ExcelHelper
from .common import DecodeMatrixDataFromBillMixin, FileMixin
from .common import assure_has_permission_of_given_business_ids, convert_business_ids_2_business_modelx_codes
from .dto import *
from ..domain.bill.aggr import BillPeriodAggr
from ..domain.report.aggr import *
from ..domain.report.repo import repo as report_repo
from ..domain.report.service import *


class ExportMixin(DecodeMatrixDataFromBillMixin, FileMixin):
    """ 导出服务 """
    @classmethod
    def _export_report_bills(cls, report_bills: List[ReportBill]) -> IO:
        """ 导出报表账单 """
        file_path = cls.__generate_file_path()
        matrix_data: List[List[Any]] = cls._decode_matrix_data_from_bills(report_bills)
        ExcelHelper.save_matrix_data_into_file(matrix_data, file_path)
        return cls._read_file(file_path)

    @classmethod
    def __generate_file_path(cls) -> str:
        return os.path.join(cls._base_path,
                            f'{const.STATIC_FT_REPORT_BILL}_{const.STATIC_FOPT_EXPORT}.{cls._file_suffix}')


class ReportApp(ExportMixin):
    """ 生成报表详情，报表详情包含概览信息和各类维度的统计数据 """
    @classmethod
    def get_reports(cls) -> List[Report]:
        """ 获取报表列表 """
        return report_repo.get_reports()

    @classmethod
    def get_report_details_filter_by_business_ids(
            cls,
            start_bill_period_id: int, end_bill_period_id: int,
            business_ids: List[int]) -> ReportDetails:

        report_bills = cls.__get_report_bills_filter_by_business_ids(
            start_bill_period_id, end_bill_period_id, business_ids)

        return cls.__get_report_details(report_bills)

    @classmethod
    def export_report_bills_filter_by_business_ids(
            cls, start_bill_period_id: int, end_bill_period_id: int,
            business_ids: List[int]) -> IO:

        report_bills = cls.__get_report_bills_filter_by_business_ids(
            start_bill_period_id, end_bill_period_id, business_ids)

        return cls._export_report_bills(report_bills)

    @classmethod
    def get_report_details_filter_by_department(
            cls, start_bill_period_id: int, end_bill_period_id: int, department_ids: List[int]) -> "ReportDetails":
        raise NotImplementedError

    @classmethod
    def __get_report_bills_filter_by_business_ids(
            cls, start_bill_period_id: int, end_bill_period_id: int, business_ids: List[int]) -> List[ReportBill]:

        assure_has_permission_of_given_business_ids(business_ids)

        business_modelx_codes = convert_business_ids_2_business_modelx_codes(business_ids)

        start_bill_period_aggr = BillPeriodAggr.get_by_id_or_raise_404(start_bill_period_id)
        end_bill_period_aggr = BillPeriodAggr.get_by_id_or_raise_404(end_bill_period_id)

        bill_periods: List[BillPeriod] = BillPeriod.query.filter(
            and_(BillPeriod.timestamp >= start_bill_period_aggr.bill_period.timestamp,
                 BillPeriod.timestamp <= end_bill_period_aggr.bill_period.timestamp)).all()

        report_bills = []
        for bill_period in bill_periods:
            bill_period_aggr = BillPeriodAggr(bill_period)

            if bill_period_aggr.is_locked:
                report_aggr = ReportAggr.get_by_bill_period_id(bill_period.id)
                report_bills.extend(report_aggr.get_report_bills_by_business_modelx_codes(business_modelx_codes))
            else:
                raise BadRequest(f'计费周期（{bill_period_aggr.bill_period.pretty_str}）状态异常：未锁定。')

        return report_bills

    @classmethod
    def __get_report_details(cls, report_bills: List[ReportBill]) -> ReportDetails:
        """ 获取报表详情 """

        # 获取报表详情要素
        total = cls.__calc_total(report_bills)
        consumption_trend = cls.__statistic_consumption_trend(report_bills)
        business_distribution = cls.__statistic_business_distribution(report_bills)
        service_type_distribution = cls.__statistic_service_type_distribution(report_bills)
        type_level_1_distribution = cls.__statistic_type_level_1_distribution(report_bills)

        # 组装概览和趋势分布图
        overview = ReportOverview(bills=report_bills, total=total)
        plots = ReportPlots(
            consumption_trend=consumption_trend,
            business_distribution=business_distribution,
            service_type_distribution=service_type_distribution,
            type_level_1_distribution=type_level_1_distribution)

        # 组装报表详情并返回
        report_details = ReportDetails(overview=overview, plots=plots)

        return report_details

    @classmethod
    def __calc_total(cls, report_bills: List[ReportBill]) -> float:
        return ReportService.calc_total(report_bills)

    @classmethod
    def __statistic_consumption_trend(cls, report_bills: List[ReportBill]) -> List[ServiceTypeConsumptionTrend]:
        return ReportService.statistic_consumption_trend(report_bills)

    @classmethod
    def __statistic_business_distribution(cls, report_bills: List[ReportBill]) -> List[BusinessDataPoint]:
        return ReportService.statistic_business_distribution(report_bills)

    @classmethod
    def __statistic_service_type_distribution(cls, report_bills: List[ReportBill]) -> List[ServiceTypeDataPoint]:
        return ReportService.statistic_service_type_distribution(report_bills)

    @classmethod
    def __statistic_type_level_1_distribution(cls, report_bills: List[ReportBill]) -> List[TypeLevel1DataPoint]:
        return ReportService.statistic_type_level_1_distribution(report_bills)
