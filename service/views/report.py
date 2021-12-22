# -*- coding: utf-8 -*-

from typing import IO

from flask_restplus import Namespace
from *****_service.web.view_models import *
from *****_service.web.views import AdvModelResource, ResourceSet, route, route_set

from common.util.auth import login_check
from common.util.paginator import *****Paginator, *****PagingResult
from service.controls.apps.report import ReportApp
from service.models.bill_period import BillPeriod
from service.controls.apps.user import wrap_assure_is_admin_or_is_any_roles

from .common import ExportMixin


api = Namespace('reports')


class VM:
    get_details = make_params(
        ['start_bill_period_id', '起始计费周期ID', int, True],
        ['end_bill_period_id', '截止计费周期ID', int, True],
        ['filter_type', '过滤类型，business或department', str, True],
        ['business_ids', '业务ID列表，filter_type为business时必填', list, False],
        _location='args')


@route_set(api, '/')
class ReportRes(ExportMixin, AdvModelResource, ResourceSet):
    app = ReportApp
    model = BillPeriod

    @login_check
    @wrap_assure_is_admin_or_is_any_roles
    def get(self):
        reports = self.app.get_reports()
        return self.get_page(
            request,
            delay_page=True,
            get_list_data_list=lambda x: [report.to_dict() for report in reports])

    @login_check
    @api.expect(VM.get_details)
    @route('/details/', method='GET')
    @wrap_assure_is_admin_or_is_any_roles
    def get_details(self):

        start_bill_period_id = int(request.args.get('start_bill_period_id'))
        end_bill_period_id = int(request.args.get('end_bill_period_id'))
        business_ids = [int(id_) for id_ in request.args.get('business_ids').split(',')]

        report_details_struct = self.app.get_report_details_filter_by_business_ids(
            start_bill_period_id, end_bill_period_id, business_ids)

        bills = report_details_struct.overview.bills
        bills_paged_result = *****Paginator.paging_with_paging_params_from_request(bills)
        result = report_details_struct.asdict()
        self.__replace_with_bills_paged_result(result, bills_paged_result)

        return result

    @login_check
    @api.expect(VM.get_details)
    @route('/details/export_report_bills/', method='GET')
    @wrap_assure_is_admin_or_is_any_roles
    def export_report_bills(self):

        start_bill_period_id = int(request.args.get('start_bill_period_id'))
        end_bill_period_id = int(request.args.get('end_bill_period_id'))
        business_ids = [int(id_) for id_ in request.args.get('business_ids').split(',')]

        storage_obj: IO = self.app.export_report_bills_filter_by_business_ids(
            start_bill_period_id, end_bill_period_id, business_ids)

        return self._send_file(storage_obj.name)

    @classmethod
    def __replace_with_bills_paged_result(cls, result: dict, bills_paged_result: *****PagingResult):
        bill_dict_list = []

        result['overview']['bills'] = bills_paged_result.asdict()

        for bill in bills_paged_result.data:
            bill_dict_list.append(bill.to_dict(excludes=['type', 'parent_id']))

        result['overview']['bills']['data'] = bill_dict_list
