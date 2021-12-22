# -*- coding: utf-8 -*-
# import events, define event handler and register to event hub

from typing import Type, Optional

from werkzeug.exceptions import BadRequest

from common.util.event import event_manager, EventBase, IEventHandler
from common.util.log import get_logger
from .bill.entity import OriginalBill, LedgerBill, SplitRule
from .bill.event import \
    BillPeriodCreated, BillPeriodDeleted, \
    OriginalBillCreated, LedgerBillCreated, \
    BillPeriodOriginBillsReady, \
    OriginalBillUpdated, LedgerBillUpdated, \
    SplitRuleCreated, SplitRuleUpdated
from .bill.spec import original_bill_spec, ledger_bill_spec
from .split.spec import bill_matcher_spec, composite_split_policy_spec
from .split.iface import IBillPeriodSplitService
from .split.val_obj import CompositeSplitPolicy, BillMatcher


BillPeriodSplitService: Optional[IBillPeriodSplitService] = None


logger = get_logger('domain:event')


class OriginalBillSpecMixin:
    @classmethod
    def check_and_append_exception(cls, original_bill: OriginalBill):
        ok, err = original_bill_spec().is_satisfied_by(original_bill)
        if not ok:
            original_bill.append_exception(err)

    @classmethod
    def check_and_mark_exception(cls, original_bill: OriginalBill):
        original_bill.exception = None
        cls.check_and_append_exception(original_bill)


class LedgerBillSpecMixin:
    @classmethod
    def check_and_mark_exception(cls, ledger_bill: LedgerBill):
        ledger_bill.exception = None
        ok, err = ledger_bill_spec().is_satisfied_by(ledger_bill)
        if not ok:
            ledger_bill.exception = err


class SplitRuleSpecMixin:
    @classmethod
    def _is_valid_or_raise(cls, split_rule: SplitRule):
        composite_split_policy = CompositeSplitPolicy.get_by_split_rule(split_rule)
        bill_matcher = BillMatcher.get_by_split_rule(split_rule)

        spec = composite_split_policy_spec()
        ok, err = spec.is_satisfied_by(composite_split_policy)
        if not ok:
            raise BadRequest(err)

        spec = bill_matcher_spec()
        ok, err = spec.is_satisfied_by(bill_matcher)
        if not ok:
            raise BadRequest(err)


class OnBillPeriodCreated(IEventHandler):
    @classmethod
    def handle(cls, e: BillPeriodCreated):
        cls.__copy_split_rules_from_previous_bill_period(e)

    @classmethod
    def __copy_split_rules_from_previous_bill_period(cls, e: BillPeriodCreated):
        """ 拷贝上个计费周期的分账规则到当前计费周期 """
        created = e.aggr
        if e.aggr.previous:
            previous = e.aggr.previous
            created.set_split_rules(previous.split_rules)
        else:
            # 找不到上个计费周期，则不进行任何处理
            logger.debug(f'bill period {created.bill_period.pretty_str} created, '
                         f'previous period not found, so split rules not copied.')


class OnBillPeriodDeleted(IEventHandler):
    @classmethod
    def handle(cls, e: BillPeriodDeleted):
        """ """
        cls.__clean_split_rules(e)
        cls.__clean_original_bills(e)
        cls.__clean_ledger_bills(e)

    @classmethod
    def __clean_original_bills(cls, e: BillPeriodDeleted):
        e.aggr.set_original_bills([])

    @classmethod
    def __clean_ledger_bills(cls, e: BillPeriodDeleted):
        e.aggr.set_ledger_bills([])

    @classmethod
    def __clean_split_rules(cls, e: BillPeriodDeleted):
        e.aggr.set_split_rules([])


class OnBillPeriodOriginalBillsReady(IEventHandler):
    @classmethod
    def handle(cls, e: BillPeriodOriginBillsReady):
        cls.__split(e.aggr.bill_period.id)

    @classmethod
    def __split(cls, bill_period_id: int):
        """ 使用领域服务进行分账 """
        BillPeriodSplitService.split_original_bills_of_bill_period(bill_period_id)


class OnOriginalBillCreated(OriginalBillSpecMixin, IEventHandler):
    @classmethod
    def handle(cls, e: OriginalBillCreated):
        cls.__check_and_append_exception(e.original_bill)

    @classmethod
    def __check_and_append_exception(cls, original_bill: OriginalBill):
        cls.check_and_append_exception(original_bill)


class OnLedgerBillCreated(LedgerBillSpecMixin, IEventHandler):
    @classmethod
    def handle(cls, e: LedgerBillCreated):
        cls.__check_and_mark_exception(e.ledger_bill)

    @classmethod
    def __check_and_mark_exception(cls, ledger_bill: LedgerBill):
        cls.check_and_mark_exception(ledger_bill)


class OnSplitRuleCreated(SplitRuleSpecMixin, IEventHandler):
    @classmethod
    def handle(cls, e: SplitRuleCreated):
        cls.__is_valid_or_raise(e.split_rule)

    @classmethod
    def __is_valid_or_raise(cls, split_rule: SplitRule):
        cls._is_valid_or_raise(split_rule)


class OnOriginalBillUpdated(OriginalBillSpecMixin, IEventHandler):
    @classmethod
    def handle(cls, e: OriginalBillUpdated):
        cls.__check_and_mark_exception(e.original_bill)

    @classmethod
    def __check_and_mark_exception(cls, original_bill: OriginalBill):
        cls.check_and_mark_exception(original_bill)


class OnLedgerBillUpdated(LedgerBillSpecMixin, IEventHandler):
    @classmethod
    def handle(cls, e: LedgerBillUpdated):
        cls.__check_and_mark_exception(e.ledger_bill)

    @classmethod
    def __check_and_mark_exception(cls, ledger_bill: LedgerBill):
        cls.check_and_mark_exception(ledger_bill)


class OnSplitRuleUpdated(SplitRuleSpecMixin, IEventHandler):
    @classmethod
    def handle(cls, e: SplitRuleUpdated):
        cls.__is_valid_or_raise(e.split_rule)

    @classmethod
    def __is_valid_or_raise(cls, split_rule: SplitRule):
        cls._is_valid_or_raise(split_rule)


class EventManager:
    __event_manager = event_manager

    @classmethod
    def register_events(cls):
        to_register = {
            BillPeriodCreated: OnBillPeriodCreated,
            BillPeriodDeleted: OnBillPeriodDeleted,
            OriginalBillCreated: OnOriginalBillCreated,
            LedgerBillCreated: OnLedgerBillCreated,
            BillPeriodOriginBillsReady: OnBillPeriodOriginalBillsReady,
            OriginalBillUpdated: OnOriginalBillUpdated,
            LedgerBillUpdated: OnLedgerBillUpdated,
            SplitRuleCreated: OnSplitRuleCreated,
            SplitRuleUpdated: OnSplitRuleUpdated
        }
        for e, h in to_register.items():
            cls.__register_event(e, h)

    @classmethod
    def emit(cls, e: EventBase):
        logger.info(f'dispatching event: {e.name}, {e.arguments}.')
        # cls.__event_manager.emit(e)
        cls.__event_manager.dispatch_event(e)
        logger.info(f'dispatching event: {e.name}, {e.arguments}, done.')

    @classmethod
    def __register_event(cls, e: Type[EventBase], h: Type[IEventHandler]):
        cls.__event_manager.register(e, h)
        logger.info(f'handler registered: {e.name} --> {h.__name__}.')
