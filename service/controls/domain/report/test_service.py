# -*- coding: utf-8 -*-

import pytest

from .service import *


@pytest.fixture
def report_bills_belongs_to_bill_periods(bill_period_aggr_factory, report_bill_factory) -> List[ReportBill]:
    bill_period_aggr1 = bill_period_aggr_factory(year=2021, month=10)
    bill_period_aggr2 = bill_period_aggr_factory(year=2021, month=11)

    report_bills: List[ReportBill] = []

    report_bills_of_bill_period_1 = [
        report_bill_factory(
            bill_period_id=bill_period_aggr1.bill_period.id, actually_paid=200000.0, business_modelx_code='b1'),
        report_bill_factory(
            bill_period_id=bill_period_aggr1.bill_period.id, actually_paid=300000.0, service_type='st1'),
        report_bill_factory(
            bill_period_id=bill_period_aggr1.bill_period.id, actually_paid=500000.0, type_level_1='tl1'),
    ]
    report_bills.extend(report_bills_of_bill_period_1)

    report_bills_of_bill_period_2 = [
        report_bill_factory(
            bill_period_id=bill_period_aggr2.bill_period.id, actually_paid=20000.0, business_modelx_code='b1'),
        report_bill_factory(
            bill_period_id=bill_period_aggr2.bill_period.id, actually_paid=30000.0, service_type='st1'),
        report_bill_factory(
            bill_period_id=bill_period_aggr2.bill_period.id, actually_paid=50000.0, type_level_1='tl1'),
    ]
    report_bills.extend(report_bills_of_bill_period_2)

    return report_bills


class TestReportService:
    def test_calc_total(self, report_bills_belongs_to_bill_periods):
        report_bills = report_bills_belongs_to_bill_periods
        assert ReportService.calc_total(report_bills) == 1100000.0

    def test_statistic_consumption_trend(self, report_bills_belongs_to_bill_periods):
        report_bills = report_bills_belongs_to_bill_periods
        res: List[ServiceTypeConsumptionTrend] = ReportService.statistic_consumption_trend(report_bills)

        assert len(res) > 0

        service_type_consumption_trend = res[0]
        assert len(service_type_consumption_trend.data) > 0

        bill_period_data_point = service_type_consumption_trend.data[0]
        assert bill_period_data_point.bill_period and bill_period_data_point.total

    def test_statistic_business_distribution(self, report_bills_belongs_to_bill_periods):
        report_bills = report_bills_belongs_to_bill_periods
        res: List[BusinessDataPoint] = ReportService.statistic_business_distribution(report_bills)

        assert len(res) == 2

        for p in res:
            if p.business is None:
                assert p.total == 880000.0

            if p.business == 'bi':
                assert p.total == 220000.0

    def test_statistic_service_type_distribution(self, report_bills_belongs_to_bill_periods):
        report_bills = report_bills_belongs_to_bill_periods
        res: List[ServiceTypeDataPoint] = ReportService.statistic_service_type_distribution(report_bills)

        assert len(res) == 2

        for p in res:
            if p.service_type is None:
                assert p.total == 770000.0

            if p.service_type == 'st1':
                assert p.total == 330000.0

    def test_statistic_type_level_1_distribution(self, report_bills_belongs_to_bill_periods):
        report_bills = report_bills_belongs_to_bill_periods
        res: List[TypeLevel1DataPoint] = ReportService.statistic_type_level_1_distribution(report_bills)

        assert len(res) == 2

        for p in res:
            if p.type_level_1 is None:
                assert p.total == 550000.0

            if p.type_level_1 == 'tl1':
                assert p.total == 550000.0


class TestBillPeriodDataPoint:
    def test_create(self):
        # TODO 无法正常初始化属性，暂时通过实例话后设置属性的方式设置规避
        p = BillPeriodDataPoint(total=1.0)
        assert p.total == 1.0
