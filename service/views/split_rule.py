# -*- coding: utf-8 -*-

from flask_restplus import Namespace
from *****_service.web.static import HTTP_OK
from *****_service.web.view_models import *
from *****_service.web.views import AdvModelResource, ResourceSet, route, route_set
from *****_service.log_service import wrap_log

from common.util.auth import login_check
from service.controls import *
from service.controls.apps.user import wrap_assure_is_admin_or_is_commercial

api = Namespace('split_rules')


class VM:
    model = make_model(api, SplitRule)
    post = model
    patch = model


@route_set(api, '/')
class ProviderRes(AdvModelResource, ResourceSet):
    __res_type = 'split_rule'

    model = SplitRule
    control = SplitRuleCtl

    select_fields = ['id', 'bill_matchers', 'split_policy', 'desc']
    filter_fields = ['bill_period_id']

    @login_check
    @wrap_assure_is_admin_or_is_commercial
    @api.expect(page_model_args)
    @api.response(200, 'Success', [VM.model])
    def get(self):
        return self.get_page(request)

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
