# -*- coding: utf-8 -*-

from flask_restplus import Namespace
from *****_service.web.static import HTTP_OK
from *****_service.web.view_models import *
from *****_service.web.views import AdvModelResource, ResourceSet, route, route_set
from *****_service.log_service import wrap_log

from common.util.auth import login_check
from service.controls import *
from service.controls.apps.user import wrap_assure_is_admin_or_is_commercial

api = Namespace('users')


class VM:
    model = make_model(api, User)
    post = make_params(
        ['email', '邮箱', str, True],
        ['is_admin', '是否管理员', bool, True],
        ['role', '角色，非管理员时必填', str, False],
        ['business_ids', '业务ID列表，非管理员时必填', list, False],
        _location='form')
    patch = model


@route_set(api, '/')
class UserRes(AdvModelResource, ResourceSet):
    __res_type = 'user'

    model = User
    control = UserCtl

    select_fields = ['id', 'email', 'business_ids']
    filter_fields = ['is_admin', 'role']

    @login_check
    @api.expect(page_model_args)
    @api.response(200, 'Success', [VM.model])
    def get(self):
        return self.get_page(request)

    @login_check
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=__res_type)
    @api.expect(VM.post)
    @api.response(200, 'Success', VM.model)
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
    @api.response(200, 'Success')
    @route('/uc_org_users/', method='GET')
    def get_uc_org_users(self):

        def get_list_data_list(*args, **kwargs):
            return [item.to_dict() for item in self.control.get_uc_org_users()]

        return self.get_page(
            request,
            delay_page=True,
            get_list_data_list=get_list_data_list)
