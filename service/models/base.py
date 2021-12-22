# -*- coding: utf-8 -*-

from typing import Optional, Union

from werkzeug.exceptions import NotFound
from flask_sqlalchemy import SQLAlchemy
from *****_service.app import *****App
from *****_service.model.base import BaseModel
from sqla_softdelete import SoftDeleteMixin
from sqlalchemy.orm import scoped_session, Session


db: Optional[SQLAlchemy] = *****App.db
db_session: Union[scoped_session, Session] = *****App.db.session
*****BaseModel: BaseModel = *****App.db.Model


class ModelBase(SoftDeleteMixin, *****BaseModel):
    __abstract__ = True

    def to_dict(self, *args, **kwargs):
        res = *****BaseModel.to_dict(self, *args, **kwargs)

        res.pop('deleted_at')
        return res

    @classmethod
    def raise_not_found(cls, **kwargs):
        raise NotFound(f'{cls.__name__}({kwargs}) not found.')
