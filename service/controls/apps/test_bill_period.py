# -*- coding: utf-8-

import os
import pytest
from werkzeug.exceptions import BadRequest

import common.static as const
import common.util.decimal as decimal
from .bill_period import BillPeriodApp, BillPeriodAggr


def init_businesses(monkeypatch):
    # 初始化业务
    from service.controls.apps import BusinessApp
    from *****_service.modelx_service import ModelxServiceRpc
    from .test_meta import modelx_entities_get
    monkeypatch.setattr(ModelxServiceRpc, 'entities_get', modelx_entities_get)
    BusinessApp.sync()


@pytest.fixture
def original_bills(original_bill_factory, bill_subject, provider):
    res = list()
    res.append(original_bill_factory(
        bill_subject_name='b1',
        provider_name='p1',
        actually_paid=1000000.00))
    return res


@pytest.fixture
def providers(provider_factory):
    provider_factory(name="上海七牛")
    provider_factory(name="尚云")


@pytest.fixture
def bill_subjects(bill_subject_factory):
    bill_subject_factory(name="广州****")
    bill_subject_factory(name="广州****")


@pytest.fixture
def split_rules(split_rule_factory):
    res = list()
    res.append(
        split_rule_factory(
            bill_matchers=dict(provider_name='p1'),
            split_policy=dict(
                type=const.SPLIT_TYPE_COMP,
                configs=[
                    dict(
                        type=const.SPLIT_TYPE_FIXED,
                        configs=dict(
                            business='*****',
                            value=500000
                        )
                    ),
                    dict(
                        type=const.SPLIT_TYPE_PROP,
                        configs=dict(
                            business='********',
                            percent='20%'
                        )
                    ),
                    dict(
                        type=const.SPLIT_TYPE_PROP,
                        configs=dict(
                            business='payment',
                            percent='80%'
                        )
                    )
                ]
            )
        )
    )
    return res


@pytest.fixture
def bill_period_aggr_with_original_bills_and_split_rules(monkeypatch, bill_period_aggr, original_bills, split_rules):
    init_businesses(monkeypatch)

    aggr = bill_period_aggr
    aggr.set_original_bills(original_bills)
    aggr.set_split_rules(split_rules)
    return aggr


def not_has_sensitive_excel_file_of_original_bills() -> bool:
    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/2021-10_原始账单_敏感.xlsx')
    return not os.path.exists(fp)


class TestBillPeriodApp:
    def test_split(self, bill_period_aggr_with_original_bills_and_split_rules):
        aggr = bill_period_aggr_with_original_bills_and_split_rules

        assert len(aggr.original_bills) == 1
        assert len(aggr.split_rules) == 1
        assert len(aggr.ledger_bills) == 0

        BillPeriodApp.split(aggr.bill_period.id)

        assert len(aggr.ledger_bills) == 3
        total = decimal.quantize(sum([ledger_bill.actually_paid for ledger_bill in aggr.ledger_bills]))
        assert total == aggr.original_bills[0].actually_paid

    @pytest.mark.skipif(not_has_sensitive_excel_file_of_original_bills(), reason="未发现未脱敏的完整月计费周期账单文件")
    def test_split_2(self, monkeypatch, shared_datadir, bill_subject_factory, provider_factory, bill_period_aggr):
        """ 使用12月测试数据测试，修复decimal相关异常 """
        aggr: BillPeriodAggr = bill_period_aggr

        init_businesses(monkeypatch)

        # 初始化计费主体
        for name in ('TIYA', 'NASHOR', '淮安****', '广州****', '广州****'):
            bill_subject_factory(name=name)

        # 初始化供应商
        for name in ('聚梦', '广州爱云', 'Zenlayer', '尚云', '锦木', '广州尚航'):
            provider_factory(name=name)

        # 导入原始账单
        excel_file = shared_datadir / '2021-12_原始账单_敏感.xlsx'

        with excel_file.open(mode='rb') as storage_obj:
            BillPeriodApp.import_original_bills_from_storage_obj(storage_obj, aggr.bill_period.id)

        # 导入分账规则
        excel_file = shared_datadir / '2021-12_分账规则.xlsx'

        with excel_file.open(mode='rb') as storage_obj:
            BillPeriodApp.import_split_rules_from_storage_obj(storage_obj, aggr.bill_period.id)

        BillPeriodApp.split(aggr.bill_period.id)

    @pytest.mark.skipif(not_has_sensitive_excel_file_of_original_bills(), reason="未发现未脱敏的完整月计费周期账单文件")
    def test_import_original_bills_from_storage_obj(self, bill_period_aggr: BillPeriodAggr, shared_datadir):
        """ 测试未脱敏的完整月计费周期账单文件导入，该文件仅在本地，不入库，故测试时发现没有该文件则自动跳过 """

        assert len(bill_period_aggr.original_bills) == 0

        excel_file = shared_datadir / '2021-10_原始账单_敏感.xlsx'

        with excel_file.open(mode='rb') as storage_obj:
            BillPeriodApp.import_original_bills_from_storage_obj(storage_obj, bill_period_aggr.bill_period.id)

        assert len(bill_period_aggr.original_bills) > 0

    @pytest.mark.skipif(not_has_sensitive_excel_file_of_original_bills(), reason="未发现未脱敏的完整月计费周期账单文件")
    def test_import_original_bills_from_storage_obj_2(self, bill_period_aggr: BillPeriodAggr, shared_datadir):
        """ 测试未脱敏的完整月计费周期账单文件导入，该文件仅在本地，不入库，故测试时发现没有该文件则自动跳过 """

        assert len(bill_period_aggr.original_bills) == 0

        excel_file = shared_datadir / '2021-11_原始账单_敏感.xlsx'

        with excel_file.open(mode='rb') as storage_obj:
            BillPeriodApp.import_original_bills_from_storage_obj(storage_obj, bill_period_aggr.bill_period.id)

        assert len(bill_period_aggr.original_bills) > 0

    def test_import_original_bills_from_storage_obj_3(self, bill_period_aggr: BillPeriodAggr, shared_datadir):
        """ 脱敏数据导入测试 """

        assert len(bill_period_aggr.original_bills) == 0

        excel_file = shared_datadir / '2021-10_原始账单_脱敏.xlsx'

        with excel_file.open(mode='rb') as storage_obj:
            BillPeriodApp.import_original_bills_from_storage_obj(storage_obj, bill_period_aggr.bill_period.id)

        assert len(bill_period_aggr.original_bills) > 0

        original_bill = bill_period_aggr.original_bills[0]
        assert original_bill.total and original_bill.total > 0
        assert original_bill.actually_paid and original_bill.actually_paid > 0

    def test_import_split_rules_from_storage_obj(self, providers, bill_subjects, bill_period_aggr: BillPeriodAggr, shared_datadir):
        assert len(bill_period_aggr.split_rules) == 0

        excel_file = shared_datadir / '2021-10_分账规则.xlsx'

        with excel_file.open(mode='rb') as storage_obj:
            BillPeriodApp.import_split_rules_from_storage_obj(storage_obj, bill_period_aggr.bill_period.id)

        assert len(bill_period_aggr.split_rules) > 0

    def test_import_split_rules_from_storage_obj_2(self, bill_period_aggr: BillPeriodAggr, shared_datadir):
        """ 因比例之和不为1而失败 """
        assert len(bill_period_aggr.split_rules) == 0

        excel_file = shared_datadir / '2021-10_分账规则_比例之和非1.xlsx'

        with excel_file.open(mode='rb') as storage_obj:
            with pytest.raises(BadRequest):
                BillPeriodApp.import_split_rules_from_storage_obj(storage_obj, bill_period_aggr.bill_period.id)

    def test_import_split_rules_from_storage_obj_3(
            self,
            bill_subjects, providers, monkeypatch,
            bill_period_aggr: BillPeriodAggr, shared_datadir):
        """ 排查线上环境导入分账规则漏字段问题 """
        assert len(bill_period_aggr.split_rules) == 0

        init_businesses(monkeypatch)

        excel_file = shared_datadir / '2021-11_分账规则_字段校验.xlsx'

        with excel_file.open(mode='rb') as storage_obj:
            BillPeriodApp.import_split_rules_from_storage_obj(storage_obj, bill_period_aggr.bill_period.id)
            assert len(bill_period_aggr.split_rules) == 1
            r = bill_period_aggr.split_rules[0]
            assert r.bill_matchers['service_type'] == 'IDC'
            assert r.bill_matchers['service_name'] == 'fake'
            assert r.bill_matchers['service_details'] == 'fake'
            assert r.bill_matchers['tag1'] == 'tag1'
            assert r.bill_matchers['tag2'] == 'tag2'
            assert r.bill_matchers['tag3'] == 'tag3'
            assert r.bill_matchers['tag4'] == 'tag4'
            assert r.bill_matchers['tag5'] == 'tag5'

    def test_export_original_bills(self, bill_period_aggr_with_original_bills_and_split_rules, bill_period_aggr):
        from_aggr = bill_period_aggr_with_original_bills_and_split_rules
        to_aggr = bill_period_aggr

        storage_obj = BillPeriodApp.export_original_bills(from_aggr.bill_period.id)

        BillPeriodApp.import_original_bills_from_storage_obj(storage_obj, to_aggr.bill_period.id)

        assert len(from_aggr.original_bills) == len(to_aggr.original_bills)

    def test_export_ledger_bills(self, bill_period_aggr_factory, ledger_bill):
        from_aggr = bill_period_aggr_factory(year=2021, month=11)
        to_aggr = bill_period_aggr_factory(year=2021, month=12)

        from_aggr.set_ledger_bills([ledger_bill])
        assert len(from_aggr.ledger_bills) > 0

        storage_obj = BillPeriodApp.export_ledger_bills(from_aggr.bill_period.id)
        BillPeriodApp.import_original_bills_from_storage_obj(storage_obj, to_aggr.bill_period.id)

        assert len(from_aggr.ledger_bills) == len(to_aggr.original_bills)

    def test_export_ledger_bills_2(self, bill_period_aggr):
        """ 因缺少数据导出失败 """
        aggr = bill_period_aggr

        with pytest.raises(BadRequest):
            BillPeriodApp.export_ledger_bills(aggr.bill_period.id)
