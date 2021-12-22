# -*- coding: utf-8 -*-

import os
from typing import List, IO, Any

from werkzeug.exceptions import BadRequest, Conflict

import common.static as const
from common.util.excel import ExcelHelper, Workbook
from service.models import *
from ..domain.bill.aggr import BillPeriodAggr
from ..domain.bill.spec import original_bill_spec
from ..domain.split.service import BillPeriodSplitService
from .dto import SimpleSplitRule
from .common import FileMixin, DecodeMatrixDataFromBillMixin


class ImportAndExportMixin(DecodeMatrixDataFromBillMixin, FileMixin):
    """ 导入导出服务 """

    __split_rule_header_cn_2_en: dict = {
        '合同编号': 'contract_id',
        '供应商': 'provider_name',
        '计费主体': 'bill_subject_name',
        '服务类型': 'service_type',
        '服务名称': 'service_name',
        '服务细项': 'service_details',
        '备注': 'desc',
        '标签一': 'tag1',
        '标签二': 'tag2',
        '标签三': 'tag3',
        '标签四': 'tag4',
        '标签五': 'tag5',
        '分摊策略': 'split_policy'
    }

    __path_of_original_bills_standard_template_file = os.path.join(const.STATIC_PATH, '原始账单导入模板2021.12.17.xlsx')
    __path_of_split_rules_standard_template_file = os.path.join(const.STATIC_PATH, '分账规则模板2021.12.21.xlsx')

    @classmethod
    def import_original_bills_from_storage_obj(cls, storage_obj: IO, bill_period_id: int):
        """ 导入原始账单到指定计费周期 """

        bill_period_aggr: BillPeriodAggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)

        # 储存文件，并加载数据
        file_path = cls.__generate_file_path(bill_period_aggr, const.STATIC_FOPT_IMPORT, const.STATIC_FT_ORIGINAL_BILL)
        cls._save_file(storage_obj, file_path)

        matrix_data = cls.__load_matrix_data_of_xlsx_file(file_path)
        if len(matrix_data) <= 1:
            raise BadRequest('未能解析到原始账单条目，请检查文件，重新上传。')

        # 解析原始账单条目
        original_bills: List[OriginalBill] = cls.__decode_original_bills_from_matrix_data(matrix_data)

        # 导入至计费周期内
        bill_period_aggr.set_original_bills(original_bills)

    @classmethod
    def import_split_rules_from_storage_obj(cls, storage_obj: IO, bill_period_id: int):
        """ 导入分账规则到指定计费周期 """
        bill_period_aggr: BillPeriodAggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)

        # 储存文件，并加载数据
        file_path = cls.__generate_file_path(bill_period_aggr, const.STATIC_FOPT_IMPORT, const.STATIC_FT_SPLIT_RULE)
        cls._save_file(storage_obj, file_path)

        matrix_data = cls.__load_matrix_data_of_xlsx_file(file_path)
        if len(matrix_data) <= 1:
            raise BadRequest('未能解析到分账规则条目，请检查文件，重新上传。')

        # 解析分账规则条目
        split_rules: List[SplitRule] = cls.__decode_split_rules_from_matrix_data(matrix_data)

        # 导入至计费周期内
        bill_period_aggr.set_split_rules(split_rules)

    @classmethod
    def export_original_bills(cls, bill_period_id: int) -> IO:
        """ 导出指定计费周期的原始账单 """
        bill_period_aggr: BillPeriodAggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)
        file_path = cls.__generate_file_path(bill_period_aggr, const.STATIC_FOPT_EXPORT, const.STATIC_FT_ORIGINAL_BILL)
        matrix_data: List[List[Any]] = cls._decode_matrix_data_from_bills(bill_period_aggr.original_bills)
        ExcelHelper.save_matrix_data_into_file(matrix_data, file_path)
        return cls._read_file(file_path)

    @classmethod
    def export_ledger_bills(cls, bill_period_id: int) -> IO:
        """ 导出指定计费周期的总账账单 """
        bill_period_aggr: BillPeriodAggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)
        file_path = cls.__generate_file_path(bill_period_aggr, const.STATIC_FOPT_EXPORT, const.STATIC_FT_LEDGER_BILL)
        matrix_data: List[List[Any]] = cls._decode_matrix_data_from_bills(bill_period_aggr.ledger_bills)
        ExcelHelper.save_matrix_data_into_file(matrix_data, file_path)
        return cls._read_file(file_path)

    @classmethod
    def export_original_bills_standard_template(cls) -> IO:
        """ 导出原始账单标准模板 """
        return cls._read_file(cls.__path_of_original_bills_standard_template_file)

    @classmethod
    def export_split_rules_standard_template(cls) -> IO:
        """ 导出分账规则标准模板 """
        return cls._read_file(cls.__path_of_split_rules_standard_template_file)

    @classmethod
    def __decode_original_bills_from_matrix_data(cls, matrix_data: List[List[Any]]) -> List[OriginalBill]:
        """ 从excel文件文本字符串中解析出原始账单列表 """
        original_bills: List[OriginalBill] = []

        headers = matrix_data[0]
        spec = original_bill_spec()
        for line in matrix_data[1:]:

            original_bill = OriginalBill.create()
            original_bill.type = const.BILL_TYPE_ORIGINAL

            for i in range(len(line)):
                if headers[i] is None:
                    continue

                attr_name_cn = headers[i].strip()
                if attr_name_cn in cls._bill_header_cn_2_en:
                    attr_name_en = cls._bill_header_cn_2_en[attr_name_cn]
                    attr_value = line[i]
                    setattr(original_bill, attr_name_en, attr_value)

            spec.fix_known_exception_cases(original_bill)
            original_bills.append(original_bill)

        return original_bills

    @classmethod
    def __decode_split_rules_from_matrix_data(cls, matrix_data: List[List[Any]]) -> List[SplitRule]:
        """ 从excel文件文本字符串中解析出分账规则列表 """
        split_rules: List[SplitRule] = []

        headers = matrix_data[0]

        for line in matrix_data[1:]:
            simple_split_rule = SimpleSplitRule()

            for i in range(len(line)):
                if headers[i] is None:
                    continue

                attr_name_cn = headers[i].strip()
                if attr_name_cn in cls.__split_rule_header_cn_2_en:
                    attr_name_en = cls.__split_rule_header_cn_2_en[attr_name_cn]
                    attr_value = line[i]
                    setattr(simple_split_rule, attr_name_en, attr_value)

            if simple_split_rule.split_policy is None:
                raise BadRequest(f'解析分账规则失败，原因：未识别到分摊策略，请在检查确认列名正确且已填写该列后重试。')

            rule = simple_split_rule.to_split_rule()

            split_rules.append(rule)

        return split_rules

    @classmethod
    def __generate_file_path(
            cls, bill_period_aggr: BillPeriodAggr,
            op_type: const.StaticFileOpType,
            static_file_type: const.StaticFileType) -> str:
        return os.path.join(cls._base_path,
                            f'{bill_period_aggr.bill_period.pretty_str}'
                            f'_{static_file_type}_{op_type}.{cls._file_suffix}')

    @classmethod
    def __load_matrix_data_of_xlsx_file(cls, file_path: str) -> List[List[Any]]:
        """ 解析给定的文件，返回一个代表表格数据的二维数组

        :param file_path: 仅包含一个工作表的excel文件路径
        :return: 代表表格数据的二维数组
        """
        wb: Workbook = ExcelHelper.load_workbook_from_file(file_path)

        if len(wb.sheetnames) != 1:
            raise BadRequest('文件中包含多个工作表，无法解析目标，请确保上传的excel文件中仅包含一个工作表。')

        matrix_data = ExcelHelper.get_matrix_data_from_worksheet(wb.worksheets[0])

        return matrix_data


class SplitMixin:
    """ 分账服务 """
    @classmethod
    def split(cls, bill_period_id: int):
        """ 对指定计费周期进行分账

        如果存在异常的原始账单，不允许操作，需要先解决后才允许操作
        """
        aggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)

        exception_original_bills = [original_bill
                                    for original_bill in aggr.original_bills
                                    if original_bill.exception is not None]

        if len(exception_original_bills) > 0:
            raise Conflict(f'存在异常的原始账单，请处理后重试。')

        BillPeriodSplitService.split_original_bills_of_bill_period(bill_period_id)


class BillPeriodApp(ImportAndExportMixin, SplitMixin):
    """ 计费周期服务 """
    @classmethod
    def create(cls, year: int, month: int) -> BillPeriod:
        aggr = BillPeriodAggr.create(year, month)
        return aggr.bill_period

    @classmethod
    def patch(cls, bill_period_id: int, year: int, month: int, is_locked: bool):
        aggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)
        aggr.patch(year, month, is_locked)

    @classmethod
    def lock(cls, bill_period_id: int):
        aggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)
        aggr.lock()

    @classmethod
    def unlock(cls, bill_period_id: int):
        aggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)
        aggr.unlock()
