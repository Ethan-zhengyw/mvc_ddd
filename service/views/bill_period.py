# -*- coding: utf-8 -*-

import io
from flask import send_file
from flask_restplus import Namespace
from *****_service.web.static import HTTP_OK
from *****_service.web.view_models import *
from *****_service.web.views import AdvModelResource, ResourceSet, route, route_set
from *****_service.log_service import wrap_log
from werkzeug.datastructures import FileStorage

from common.util.auth import login_check
from service.controls import *
from service.controls.apps.user import wrap_assure_is_admin_or_is_commercial
from .common import ImportMixin, ExportMixin


api = Namespace('bill_periods')


class VM:
    model = make_model(api, BillPeriod)
    post = make_params(
        ['year', '年', int, True],
        ['month', '月', int, True],
        ['is_lock', '是否锁定', bool, False],
        _location='form')
    patch = post


@route_set(api, '/')
class BillPeriodRes(ImportMixin, ExportMixin, AdvModelResource, ResourceSet):
    __res_type = 'bill_period'

    model = BillPeriod
    control = BillPeriodCtl

    select_fields = ['id', 'year', 'month']
    filter_fields = ['year', 'month', 'is_locked', 'timestamp']

    # API装饰器装饰顺序约定：
    # 没有使用route装饰器的：
    #   login_check > wrap_assure_is_admin_or_is_* > expect > response > wrap_log
    # 有使用route装饰器的：
    #   因为wrap_assure_is_admin_or_is_*直接跟在login_check后，会导致请求接口返回404，但swagger能够展示，原因不明，待排查
    #   故目前约定以下顺序（待原因排查出来后调整）
    #   login_check > expect > response > route > wrap_assure_is_admin_or_is_* > wrap_log
    @login_check
    @wrap_assure_is_admin_or_is_commercial
    @api.expect(page_model_args)
    @api.response(200, 'Success', [VM.model])
    def get(self):
        return self.get_page(request)

    @login_check
    @api.expect(id_args)
    @api.response(200, HTTP_OK)
    @route('/<int:id_>/', method='GET')
    @wrap_assure_is_admin_or_is_commercial
    def get_one(self, id_):
        obj_ctl = self.control.get_or_404(id_)
        extend_fields = self.extend_fields or []
        extend_fields.append('abnormal_original_bill_cnt')
        extend_fields.append('abnormal_ledger_bill_cnt')
        return obj_ctl.to_dict(extends=extend_fields, excludes=self.exclude_fields)

    @login_check
    @wrap_assure_is_admin_or_is_commercial
    @api.expect(VM.post)
    @api.response(200, 'Success', VM.model)
    @wrap_log(resource_type=__res_type)
    def post(self):
        args = request.json
        obj_ctl = self.control.create(**args)
        return obj_ctl.to_dict(extends=self.extend_fields, excludes=self.exclude_fields)

    @login_check
    @api.expect(id_args)
    @api.response(200, HTTP_OK)
    @route('/<int:id_>/', method='DELETE')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=__res_type)
    def delete(self, id_):
        obj_ctl = self.control.get_or_404(id_)
        obj_ctl.delete()
        return HTTP_OK

    @login_check
    @api.expect(VM.patch)
    @api.response(200, 'Success', VM.model)
    @route('/<int:id_>/', method='PATCH')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=__res_type)
    def patch(self, id_):
        year = request.json.get('year', None)
        month = request.json.get('month', None)
        is_locked = request.json.get('is_locked', None)
        obj_ctl = self.control.get_or_404(id_)
        obj_ctl.patch(id_, year, month, is_locked)
        return obj_ctl.to_dict(extends=self.extend_fields, excludes=self.exclude_fields)

    @login_check
    @api.response(200, HTTP_OK)
    @route('/<int:id_>/lock/', method='POST')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=__res_type)
    def lock(self, id_):
        self.control.lock(id_)
        return HTTP_OK

    @login_check
    @api.response(200, HTTP_OK)
    @route('/<int:id_>/unlock/', method='POST')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=__res_type)
    def unlock(self, id_):
        self.control.unlock(id_)
        return HTTP_OK

    @login_check
    @api.response(200, HTTP_OK)
    @route('/<int:id_>/split/', method='POST')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=__res_type)
    def split(self, id_):
        self.control.split(id_)
        return HTTP_OK

    @login_check
    @api.response(200, HTTP_OK)
    @route('/<int:id_>/import_original_bills/', method='POST')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=__res_type)
    def import_original_bills(self, id_):
        storage_obj: IO = self._decode_file_or_raise_2()
        self.control.import_original_bills_from_storage_obj(storage_obj, id_)
        return HTTP_OK

    @login_check
    @api.response(200, HTTP_OK)
    @route('/<int:id_>/import_split_rules/', method='POST')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=__res_type)
    def import_split_rules(self, id_):
        storage_obj: IO = self._decode_file_or_raise_2()
        self.control.import_split_rules_from_storage_obj(storage_obj, id_)
        return HTTP_OK

    @login_check
    @api.response(200, HTTP_OK)
    @route('/<int:id_>/export_original_bills/', method='GET')
    @wrap_assure_is_admin_or_is_commercial
    def export_original_bills(self, id_):
        storage_obj: IO = self.control.export_original_bills(id_)
        return self._send_file(storage_obj.name)

    @login_check
    @api.response(200, HTTP_OK)
    @route('/<int:id_>/export_ledger_bills/', method='GET')
    @wrap_assure_is_admin_or_is_commercial
    def export_ledger_bills(self, id_):
        storage_obj: IO = self.control.export_ledger_bills(id_)
        return self._send_file(storage_obj.name)

    @login_check
    @api.response(200, HTTP_OK)
    @route('/standard_templates/original_bills/', method='GET')
    @wrap_assure_is_admin_or_is_commercial
    def export_original_bills_standard_template(self):
        storage_obj: IO = self.control.export_original_bills_standard_template()
        return self._send_file(storage_obj.name)

    @login_check
    @api.response(200, HTTP_OK)
    @route('/standard_templates/split_rules/', method='GET')
    @wrap_assure_is_admin_or_is_commercial
    def export_split_rules_standard_template(self):
        storage_obj: IO = self.control.export_split_rules_standard_template()
        return self._send_file(storage_obj.name)

