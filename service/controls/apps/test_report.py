# -*- coding: utf-8 -*-

import pytest

import service.controls.apps.common as common
from .report import *


@pytest.fixture
def business_1(business):
    return business


@pytest.fixture
def business_2(business_factory):
    return business_factory(name='b2', other=dict(modelx_code='b2_modelx_code'))


@pytest.fixture
def parameters_of_get_report_details_filter_by_business_ids(
        bill_period_aggr_factory, report_bill_factory,
        business_1, business_2) -> (BillPeriodAggr, BillPeriodAggr, List[int]):
    start_aggr = bill_period_aggr_factory(year=2021, month=10)
    report_bill_factory(
        bill_period_id=start_aggr.bill_period.id, actually_paid=200000.0,
        business_modelx_code=business_1.modelx_code)
    report_bill_factory(
        bill_period_id=start_aggr.bill_period.id, actually_paid=300000.0,
        service_type='st1', business_modelx_code=business_2.modelx_code)
    report_bill_factory(
        bill_period_id=start_aggr.bill_period.id, actually_paid=500000.0, type_level_1='tl1')
    start_aggr.lock()

    end_aggr = bill_period_aggr_factory(year=2021, month=11)
    report_bill_factory(
        bill_period_id=end_aggr.bill_period.id, actually_paid=20000.0,
        business_modelx_code=business_1.modelx_code)
    report_bill_factory(
        bill_period_id=end_aggr.bill_period.id, actually_paid=30000.0,
        service_type='st1', business_modelx_code=business_2.modelx_code)
    report_bill_factory(
        bill_period_id=end_aggr.bill_period.id, actually_paid=50000.0, type_level_1='tl1')
    end_aggr.lock()

    return start_aggr, end_aggr, [business_1.id, business_2.id]


def mock_get_user_info():
    class MockAdmin:
        is_admin = True

    return MockAdmin()


class TestReportApp:
    def test_get_report_details_filter_by_business_ids(
            self,
            monkeypatch,
            parameters_of_get_report_details_filter_by_business_ids):
        start_aggr, end_aggr, bids = parameters_of_get_report_details_filter_by_business_ids

        monkeypatch.setattr(common, 'get_user_info', mock_get_user_info)

        details = ReportApp.get_report_details_filter_by_business_ids(
            start_aggr.bill_period.id, end_aggr.bill_period.id, bids)

        assert len(details.overview.bills) == 4

        assert details.overview.total == 550000.0

        assert len(details.plots.consumption_trend) == 2          # st1 and None
        assert len(details.plots.service_type_distribution) == 2  # st1 and None
        assert len(details.plots.business_distribution) == 2      # b1 and b2
        assert len(details.plots.type_level_1_distribution) == 1  # None

    def test_get_report_details_filter_by_business_ids_2(
            self,
            monkeypatch,
            parameters_of_get_report_details_filter_by_business_ids):
        """ id为0，表示业务id为None账单 """
        start_aggr, end_aggr, bids = parameters_of_get_report_details_filter_by_business_ids
        bids.append(0)

        monkeypatch.setattr(common, 'get_user_info', mock_get_user_info)

        details = ReportApp.get_report_details_filter_by_business_ids(
            start_aggr.bill_period.id, end_aggr.bill_period.id, bids)

        assert len(details.overview.bills) == 6

        assert details.overview.total == 1100000.0

        assert len(details.plots.consumption_trend) == 2          # st1 and None
        assert len(details.plots.service_type_distribution) == 2  # st1 and None
        assert len(details.plots.business_distribution) == 3      # b1 and b2 and None
        assert len(details.plots.type_level_1_distribution) == 2  # t1 and None

    def test_get_report_details_filter_by_business_ids_3(self, monkeypatch, bill_period_aggr):
        """ 因计费周期状态异常而失败 """
        start_aggr = bill_period_aggr
        end_aggr = bill_period_aggr
        bids = []

        with pytest.raises(BadRequest):

            monkeypatch.setattr(common, 'get_user_info', mock_get_user_info)

            ReportApp.get_report_details_filter_by_business_ids(
                start_aggr.bill_period.id, end_aggr.bill_period.id, bids)
