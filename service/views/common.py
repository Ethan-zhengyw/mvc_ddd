# -*- coding: utf-8 -*-

import io
from typing import IO

from werkzeug.exceptions import BadRequest
from flask import send_file
from *****_service.web.view_models import *
from werkzeug.datastructures import FileStorage


class ImportMixin:
    @classmethod
    def _decode_file_or_raise_2(cls) -> IO:
        if request.data:
            return io.BytesIO(request.data)
        else:
            try:
                return cls._decode_file_or_raise()
            except BadRequest as e:
                raise e

    @staticmethod
    def _decode_file_or_raise() -> IO:
        # check if the post request has the file part
        if 'file' not in request.files and '' not in request.files:
            raise BadRequest('未检测到账单文件，请检查。')

        file: FileStorage = request.files.get('file', None) or request.files.get('')
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if not file or file.filename == '':
            raise BadRequest('未获取到账单文件，请检查。')

        allowed_extensions = ['xlsx']

        def allowed_file(fn):
            return '.' in fn and \
                   fn.rsplit('.', 1)[1].lower() in allowed_extensions

        if allowed_file(file.filename):
            return file.stream
        else:
            raise BadRequest(f'非法文件类型，请上传以下类型文件：{",".join(allowed_extensions)}')


class ExportMixin:
    @staticmethod
    def _send_file(fp: str):
        return send_file(fp)
