# -*- coding: utf-8 -*-

from flask_restplus import Namespace
from *****_service.web.static import HTTP_OK
from *****_service.web.view_models import *
from *****_service.web.views import AdvModelResource, ResourceSet, route, route_set
from *****_service.log_service import wrap_log

from common.util.auth import login_check
from service.controls import *
from service.controls.apps.user import wrap_assure_is_admin_or_is_commercial


api = Namespace('ledger_bills')


class VM:
    model = make_model(api, LedgerBill)
    post = model
    patch = model


@route_set(api, '/')
class LedgerBillRes(AdvModelResource, ResourceSet):
    __res_type = 'ledger_bill'

    model = LedgerBill
    control = LedgerBillCtl

    select_fields = [
        'contract_id',
        'provider_name',
        'bill_subject_name',
        'service_type',
        'service_name',
        'service_details',
        'desc'
    ]
    filter_fields = ['business_name', 'bill_period_id', 'is_exception', 'business_modelx_code']
    exclude_fields = ['type']

    @login_check
    @wrap_assure_is_admin_or_is_commercial
    @api.expect(page_model_args)
    @api.response(200, 'Success', [VM.model])
    def get(self):
        return self.get_page(
            request,
            query_op=lambda q: q.filter_by(type=const.BILL_TYPE_LEDGER))

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
        args = request.json
        obj_ctl = self.control.get_or_404(id_)
        obj_ctl.patch(**args)
        return obj_ctl.to_dict(extends=self.extend_fields, excludes=self.exclude_fields)

    @login_check
    @api.response(200, 'Success', VM.model)
    @route('/<int:id_>/', method='GET')
    @wrap_assure_is_admin_or_is_commercial
    def get_one(self, id_):
        obj_ctl = self.control.get_or_404(id_)
        return obj_ctl.to_dict(extends=self.extend_fields, excludes=self.exclude_fields)

    @login_check
    @api.expect([VM.model])
    @api.response(200, HTTP_OK)
    @route('/<int:id_>/split/', method='POST')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=__res_type)
    def split(self, id_):
        args = request.json

        ledger_bills = []

        for kwargs in args:
            kwargs['type'] = const.BILL_TYPE_LEDGER
            ledger_bills.append(LedgerBill.create(**kwargs))

        self.control.split(id_, ledger_bills)

        return HTTP_OK
