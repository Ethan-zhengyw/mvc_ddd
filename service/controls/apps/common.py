# -*- coding: utf-8 -*-

from typing import List, IO, Any, Optional

from common.util.auth import get_user_info, User, get_uc_user
import common.static as const
from service.models import *
from ..domain.meta.repo import repo as meta_repo
from ..domain.user.aggr import UserAggr


def assure_has_permission_of_given_business_ids(business_ids: List[int]):
    user_info = get_user_info()

    if not user_info.is_admin:
        uc_user: User = get_uc_user()
        user_aggr: UserAggr = UserAggr.get_by_email_or_404(uc_user.email)
        user_aggr.assure_has_permission_of_all_given_business_ids(business_ids)


def convert_business_ids_2_business_modelx_codes(business_ids: List[int]) -> List[Optional[str]]:
    business_modelx_codes: List[Optional[str]] = [business.modelx_code
                                                  for business in meta_repo.get_businesses()
                                                  if business.id in business_ids]
    if 0 in business_ids:
        business_modelx_codes.append(None)

    return business_modelx_codes


class FileMixin:
    """ 文件服务基础 """

    _base_path = const.STATIC_PATH
    _file_suffix = 'xlsx'

    @classmethod
    def _read_file(cls, file_path: str) -> Optional[IO]:
        return open(file_path, mode="rb")

    @classmethod
    def _save_file(cls, storage_obj: IO, file_path: str):
        with open(file_path, mode="wb") as f:
            f.write(storage_obj.read())


class DecodeMatrixDataFromBillMixin:

    _bill_header_cn_2_en: dict = {
        '合同编号': 'contract_id',
        '供应商': 'provider_name',
        '计费主体': 'bill_subject_name',
        '服务类型': 'service_type',
        '服务名称': 'service_name',
        '服务细项': 'service_details',
        '单价': 'unit_price',
        '计费单位': 'bill_unit',
        '统计量': 'statistic_cnt',
        '统计单位': 'statistic_unit',
        '总计': 'total',
        '折扣': 'discount',
        '实付金额': 'actually_paid',
        '业务': 'business_modelx_code',
        '备注': 'desc',
        '标签一': 'tag1',
        '标签二': 'tag2',
        '标签三': 'tag3',
        '标签四': 'tag4',
        '标签五': 'tag5',
    }

    @classmethod
    def _decode_matrix_data_from_bills(cls, bills: List[Bill]) -> List[List[Any]]:
        headers = list(cls._bill_header_cn_2_en.keys())

        matrix_data: List[List[Any]] = [headers]

        for bill_ in bills:

            row = []
            for attr_name_cn in headers:
                attr_name_en = cls._bill_header_cn_2_en[attr_name_cn]
                attr_val = getattr(bill_, attr_name_en, None)
                row.append(attr_val)

            matrix_data.append(row)

        return matrix_data
