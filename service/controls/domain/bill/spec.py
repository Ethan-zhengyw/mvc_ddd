# -*- coding: utf-8 -*-

from typing import List, Optional

from sqlalchemy.schema import Column

from .entity import *
from ..meta import MetaSpec, meta_spec


class BillSpec:
    def __init__(self, meta_spec_: MetaSpec):
        self.__meta_spec = meta_spec_

    @property
    def businesses(self) -> List[str]:
        return self.__meta_spec.businesses

    def is_satisfied_by(self, bill: Bill) -> (bool, Optional[str]):
        ok1, err1 = self._is_business_valid(bill.business_modelx_code)
        ok2, err2 = self._is_bill_subject_valid(bill.bill_subject_name)
        ok3, err3 = self._is_provider_valid(bill.provider_name)

        if ok1 and ok2 and ok3:
            return True, None
        else:
            return False, "\n".join([str(e) for e in [err1, err2, err3] if e is not None])

    def _is_business_valid(self, business: str) -> (bool, Optional[str]):
        return self.__meta_spec.is_business_valid(business)

    def _is_bill_subject_valid(self, bill_subject: str) -> (bool, Optional[str]):
        return self.__meta_spec.is_bill_subject_valid(bill_subject)

    def _is_provider_valid(self, provider: str) -> (bool, Optional[str]):
        return self.__meta_spec.is_provider_valid(provider)


class OriginalBillAutoFixer:

    @classmethod
    def auto_fix_and_mark_exception(cls, original_bill: OriginalBill):
        """ 检测并修复已知的异常数据，并标记异常

        例如，/ 表示无，可以自动替换为空值或对应类型的默认值

        """
        # for attr in cls.__get_attrs_that_can_be_auto_fixed():
        #     auto_fix_func = getattr(cls.__dict__[f'_{cls.__name__}__auto_fix_{attr}'], '__func__')
        #     attr_value = getattr(original_bill, attr)
        #     setattr(original_bill, attr, auto_fix_func(attr_value))
        cls.__auto_fix_type_mistakes(original_bill)

    @classmethod
    def __auto_fix_type_mistakes(cls, original_bill: OriginalBill):
        """ 自动修复类型不匹配的属性，修复方法是将值置空 """
        for col_ in OriginalBill.iter_columns():
            col: Column = col_

            if col.name in ["create_time", "update_time", "deleted_at"]:
                continue

            if col.name == 'actually_paid':
                cls.__auto_fix_actually_paid(original_bill)
                continue

            col_value = getattr(original_bill, col.name)

            if col_value is not None:
                col_type = col.type.python_type
                try:
                    col_type(col_value)
                except (ValueError, TypeError):
                    original_bill.append_exception(
                        f'{col.comment}="{col_value}"类型({col_type.__name__})校验不通过，已置空，请检查并更新该属性；')
                    setattr(original_bill, col.name, None)

    @classmethod
    def __auto_fix_actually_paid(cls, original_bill: OriginalBill):
        attr_name = 'actually_paid'

        actually_paid = getattr(original_bill, attr_name)
        if actually_paid is not None:
            try:
                round(float(actually_paid), 2)
            except (ValueError, TypeError):
                original_bill.append_exception(
                    f'实付金额="{actually_paid}"类型(decimal(11, 2))校验不通过，已置空，请检查并更新该属性；')
                setattr(original_bill, attr_name, None)

    # @classmethod
    # def __get_attrs_that_can_be_auto_fixed(cls) -> List[str]:
    #     attrs = []
    #
    #     for attr in cls.__dict__.keys():
    #         if attr.startswith(f'_{cls.__name__}__auto_fix_'):
    #             attrs.append(attr[attr.find('auto_fix_') + 9:])
    #
    #     return attrs
    #
    # @staticmethod
    # def __auto_fix_unit_price(val):
    #     if val == '/':
    #         return None
    #
    #     if val is not None:
    #         try:
    #             float(val)
    #         except ValueError:
    #             return None
    #
    #     return val
    #
    # @staticmethod
    # def __auto_fix_statistic_cnt(val):
    #     if val == '/':
    #         return None
    #
    #     if val is not None:
    #         try:
    #             float(val)
    #         except ValueError:
    #             return None
    #
    #     return val


class OriginalBillSpec(BillSpec):
    def __init__(self, meta_spec_: MetaSpec):
        super().__init__(meta_spec_)
        self.auto_fixer = OriginalBillAutoFixer

    def fix_known_exception_cases(self, original_bill: OriginalBill):
        self.auto_fixer.auto_fix_and_mark_exception(original_bill)


class LedgerBillSpec(BillSpec):
    def __init__(self, meta_spec_: MetaSpec):
        super().__init__(meta_spec_)

    def _is_business_valid(self, business: str) -> (bool, Optional[str]):
        if business in self.businesses:
            return True, None
        else:
            return False, f'业务名称"{business}"非法，参考值：{"、".join(self.businesses[:3])}...'


def original_bill_spec() -> OriginalBillSpec:
    return OriginalBillSpec(meta_spec())


def ledger_bill_spec() -> LedgerBillSpec:
    return LedgerBillSpec(meta_spec())
