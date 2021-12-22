# -*- coding: utf-8 -*-

from typing import List

import pytest

import common.static as const
from .models import *
from .controls.domain.bill.aggr import BillPeriodAggr
from .controls.domain.bill.entity import OriginalBill, SplitRule, LedgerBill


# content of plugins/example_plugin.py
def pytest_configure(config):
    print('setting up events...')
    from service.controls.domain.event import EventManager
    EventManager.register_events()


@pytest.fixture
def bill_period_aggr_factory():

    aggrs: List[BillPeriodAggr] = []

    def create_bill_period_and_return_aggr(year, month):
        aggr = BillPeriodAggr.create(year, month)
        print(f'bill_period({aggr.bill_period.pretty_str}) created.')
        aggrs.append(aggr)
        return aggr
    yield create_bill_period_and_return_aggr

    for item in aggrs:
        item.delete()
        print(f'bill_period({item.bill_period.pretty_str}) deleted.')


@pytest.fixture
def bill_period_aggr(bill_period_aggr_factory):
    return bill_period_aggr_factory(2021, 11)


@pytest.fixture
def original_bill_factory():

    original_bills: List[LedgerBill] = []

    def create_original_bill(**kwargs):
        original_bill = OriginalBill.create(type=const.BILL_TYPE_ORIGINAL, **kwargs)
        print(f'original_bill({original_bill.id}) created.')
        original_bills.append(original_bill)
        return original_bill
    yield create_original_bill

    for item in original_bills:
        item.delete()
        print(f'original_bill({item.id}) deleted.')


@pytest.fixture
def original_bill(original_bill_factory):
    return original_bill_factory(provider_name='p1', actually_paid=1000000)


@pytest.fixture
def ledger_bill_factory():

    ledger_bills: List[LedgerBill] = []

    def create_ledger_bill(**kwargs):
        ledger_bill = LedgerBill.create(type=const.BILL_TYPE_LEDGER, **kwargs)
        print(f'ledger_bill({ledger_bill.id}) created.')
        ledger_bills.append(ledger_bill)
        return ledger_bill
    yield create_ledger_bill

    for item in ledger_bills:
        item.delete()
        print(f'ledger_bill({item.id}) deleted.')


@pytest.fixture
def ledger_bill(ledger_bill_factory):
    return ledger_bill_factory(provider_name='p1', actually_paid=1000000)


@pytest.fixture
def report_bill_factory():

    report_bills: List[LedgerBill] = []

    def create_report_bill(**kwargs):
        report_bill = LedgerBill.create(type=const.BILL_TYPE_LEDGER, **kwargs)
        print(f'report_bill({report_bill.id}) created.')
        report_bills.append(report_bill)
        return report_bill
    yield create_report_bill

    for item in report_bills:
        item.delete()
        print(f'report_bill({item.id}) deleted.')


@pytest.fixture
def split_rule_factory():

    split_rules: List[LedgerBill] = []

    def create_split_rule(**kwargs):
        split_rule = SplitRule.create(**kwargs)
        print(f'split_rule({split_rule.id}) created.')
        split_rules.append(split_rule)
        return split_rule
    yield create_split_rule

    for item in split_rules:
        item.delete()
        print(f'split_rule({item.id}) deleted.')


@pytest.fixture
def split_rule(split_rule_factory, provider):
    return split_rule_factory(
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
                        percent=0.2
                    )
                ),
                dict(
                    type=const.SPLIT_TYPE_PROP,
                    configs=dict(
                        business='payment',
                        percent=0.8
                    )
                )
            ]
        )
    )


@pytest.fixture
def business_factory():

    businesses: List[Business] = []

    def create_business(**kwargs):
        business = Business.create(type=const.META_TYPE_BUSINESS, **kwargs)
        print(f'business({business.id}) created.')
        businesses.append(business)
        return business
    yield create_business

    for item in businesses:
        item.delete()
        print(f'business({item.id}) deleted.')


@pytest.fixture
def business(business_factory):
    return business_factory(name='b1', full_name='b1_fn', other=dict(modelx_code='b1_modelx_code'))


@pytest.fixture
def bill_subject_factory():

    bill_subjects: List[Business] = []

    def create_bill_subject(**kwargs):
        bill_subject = BillSubject.create(type=const.META_TYPE_BILL_SUBJECT, **kwargs)
        print(f'bill_subject({bill_subject.id}) created.')
        bill_subjects.append(bill_subject)
        return bill_subject
    yield create_bill_subject

    for item in bill_subjects:
        item.delete()
        print(f'bill_subject({item.id}) deleted.')


@pytest.fixture
def bill_subject(bill_subject_factory):
    return bill_subject_factory(name='b1', full_name='b1_fn')


@pytest.fixture
def provider_factory():

    providers: List[Business] = []

    def create_provider(**kwargs):
        provider = Provider.create(type=const.META_TYPE_PROVIDER, **kwargs)
        print(f'provider({provider.id}) created.')
        providers.append(provider)
        return provider
    yield create_provider

    for item in providers:
        item.delete()
        print(f'provider({item.id}) deleted.')


@pytest.fixture
def provider(provider_factory):
    return provider_factory(name='p1', full_name='p1_fn')
