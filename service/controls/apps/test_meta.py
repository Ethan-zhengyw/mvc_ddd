# -*- coding: utf-8 -*-

from .meta import BusinessApp
from ..domain.meta.repo import repo

from *****_service.modelx_service import ModelxServiceRpc


def modelx_entities_get(*args, **kwargs):
    return {
        "rcode": 0,
        "data": {
            "total": 32,
            "page": 1,
            "limit": 9999,
            "count": 32,
            "data": [{
                "id": "infrastructure",
                "ver": 2,
                "name": "基础架构",
                "update_time": 1615369468.0,
                "model_code": "BUSINESS",
                "graph_id": "_ENTITY_-BUSINESS-infrastructure",
                "state": "1",
                "code": "infrastructure",
                "links": []
            }]
        },
        "msg": ""
    }


class TestBusinessApp:
    def test_sync(self, monkeypatch):
        monkeypatch.setattr(ModelxServiceRpc, 'entities_get', modelx_entities_get)

        BusinessApp.sync()
        businesses = repo.get_businesses()

        num_of_business = len(businesses)

        assert num_of_business > 0

        businesses[0].delete()
        businesses = repo.get_businesses()
        assert len(businesses) == num_of_business - 1

        BusinessApp.sync()
        businesses = repo.get_businesses()
        assert len(businesses) == num_of_business
