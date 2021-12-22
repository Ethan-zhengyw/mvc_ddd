# -*- coding: utf-8 -*-

import pytest
from ..bill.aggr import BillPeriodAggr


@pytest.fixture(params=[(2021, 9), (2021, 10), (2021, 11)])
def one_of_multiple_bill_period_aggrs(request, bill_period_aggr_factory):
    year, month = request.param
    return bill_period_aggr_factory(year, month)


class TestBillPeriodAggr:
    def test_create_aggr(self, one_of_multiple_bill_period_aggrs: BillPeriodAggr):
        aggr = one_of_multiple_bill_period_aggrs
        query_result = BillPeriodAggr.get_by_id_or_raise_404(aggr.bill_period.id)
        assert query_result is not None

    def test_previous(self, bill_period_aggr_factory):
        first = bill_period_aggr_factory(2021, 8)
        second = bill_period_aggr_factory(2021, 9)
        forth = bill_period_aggr_factory(2021, 11)
        third = bill_period_aggr_factory(2021, 10)

        assert second.previous.bill_period.id == first.bill_period.id
        assert third.previous.bill_period.id == second.bill_period.id
        assert forth.previous.bill_period.id == third.bill_period.id
