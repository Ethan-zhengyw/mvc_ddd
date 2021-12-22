# -*- coding: utf-8 -*-

from flask_restplus import Namespace
from *****_service.web.static import HTTP_OK
from *****_service.web.view_models import *
from *****_service.web.views import AdvModelResource, ResourceSet, route, route_set
from *****_service.log_service import wrap_log

from common.util.auth import login_check
from service.controls import *
from service.controls.apps.user import wrap_assure_is_admin_or_is_commercial

api = Namespace('meta', validate=True)


class VM:
    model = make_model(api, Meta)
    post = make_params(
        ['name', '名称', str, True],
        ['full_name', '全称', str, True],
        _location='form')
    patch = model


@route_set(api, '/providers/')
class ProviderRes(AdvModelResource, ResourceSet):
    model = Meta
    control = MetaCtl

    select_fields = ['id', 'name', 'full_name']  # search field list
    exclude_fields = ['other', 'type']

    @login_check
    @wrap_assure_is_admin_or_is_commercial
    @api.expect(page_model_args)
    @api.response(200, 'Success', [VM.model])
    def get(self):
        return self.get_page(request, query_op=lambda q: q.filter_by(type=const.META_TYPE_PROVIDER))

    @login_check
    @wrap_assure_is_admin_or_is_commercial
    @api.expect(VM.post)
    @api.response(200, 'Success', VM.model)
    @wrap_log(resource_type=const.META_TYPE_PROVIDER)
    def post(self):
        args = request.json
        obj_ctl = self.control.create(type=const.META_TYPE_PROVIDER, **args)
        return obj_ctl.to_dict(extends=self.extend_fields, excludes=self.exclude_fields)

    @login_check
    @api.expect(id_args)
    @api.response(200, HTTP_OK)
    @route('/providers/<int:id_>/', method='DELETE')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=const.META_TYPE_PROVIDER)
    def delete(self, id_):
        obj_ctl = self.control.get_or_404(id_)
        obj_ctl.delete()
        return HTTP_OK

    @login_check
    @api.expect(VM.post)
    @api.response(200, 'Success', VM.model)
    @route('/providers/<int:id_>/', method='PATCH')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=const.META_TYPE_PROVIDER)
    def patch(self, id_):
        args = request.json
        obj_ctl = self.control.get_or_404(id_)
        obj_ctl.patch(**args)
        return obj_ctl.to_dict(extends=self.extend_fields, excludes=self.exclude_fields)

    @login_check
    @wrap_assure_is_admin_or_is_commercial
    @api.response(200, 'Success', VM.model)
    @route('/providers/<int:id_>/', method='GET')
    def get_one(self, id_):
        obj_ctl = self.control.get_or_404(id_)
        return obj_ctl.to_dict(extends=self.extend_fields, excludes=self.exclude_fields)


@route_set(api, '/bill_subjects/')
class BillSubjectRes(AdvModelResource, ResourceSet):
    model = Meta
    control = MetaCtl

    select_fields = ['id', 'name', 'full_name']  # search field list
    exclude_fields = ['other', 'type']

    @login_check
    @wrap_assure_is_admin_or_is_commercial
    @api.expect(page_model_args)
    @api.response(200, 'Success', [VM.model])
    def get(self):
        return self.get_page(request, query_op=lambda q: q.filter_by(type=const.META_TYPE_BILL_SUBJECT))

    @login_check
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=const.META_TYPE_BILL_SUBJECT)
    @api.expect(VM.post)
    @api.response(200, 'Success', VM.model)
    def post(self):
        args = request.json
        obj_ctl = self.control.create(type=const.META_TYPE_BILL_SUBJECT, **args)
        return obj_ctl.to_dict(extends=self.extend_fields, excludes=self.exclude_fields)

    @login_check
    @api.expect(id_args)
    @api.response(200, HTTP_OK)
    @route('/bill_subjects/<int:id_>/', method='DELETE')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=const.META_TYPE_BILL_SUBJECT)
    def delete(self, id_):
        obj_ctl = self.control.get_or_404(id_)
        obj_ctl.delete()
        return HTTP_OK

    @login_check
    @api.expect(VM.patch)
    @api.response(200, 'Success', VM.model)
    @route('/bill_subjects/<int:id_>/', method='PATCH')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=const.META_TYPE_BILL_SUBJECT)
    def patch(self, id_):
        args = request.json
        obj_ctl = self.control.get_or_404(id_)
        obj_ctl.patch(**args)
        return obj_ctl.to_dict(extends=self.extend_fields, excludes=self.exclude_fields)

    @login_check
    @wrap_assure_is_admin_or_is_commercial
    @api.response(200, 'Success', VM.model)
    @route('/bill_subjects/<int:id_>/', method='GET')
    def get_one(self, id_):
        obj_ctl = self.control.get_or_404(id_)
        return obj_ctl.to_dict(extends=self.extend_fields, excludes=self.exclude_fields)


@route_set(api, '/businesses/')
class BusinessRes(AdvModelResource, ResourceSet):
    model = Meta
    control = MetaCtl

    select_fields = ['id', 'name', 'full_name', 'other']  # search field list
    exclude_fields = ['type', 'other']
    extend_fields = ['modelx_code', 'modelx_id']

    @login_check
    @api.expect(page_model_args)
    @api.response(200, 'Success', [VM.model])
    def get(self):
        return self.get_page(request, query_op=lambda q: q.filter_by(type=const.META_TYPE_BUSINESS))

    @login_check
    @api.response(200, HTTP_OK)
    @route('/businesses/sync/', method='POST')
    @wrap_assure_is_admin_or_is_commercial
    @wrap_log(resource_type=const.META_TYPE_BUSINESS)
    def sync(self):
        self.control.sync_businesses()
        return HTTP_OK
