# -*- coding: utf-8 -*-

from .val_obj import CompositePolicy


class TestCompositePolicy:
    def test_create(self):
        body = {
            "type": "composite",
            "configs": [
                {
                    "type": "fixed_value",
                    "configs": {
                        "business": "b1",
                        "value": 500000
                    }
                },
                {
                    "type": "proportional",
                    "configs": {
                        "business": "b2",
                        "percent": 0.2
                    }
                },
                {
                    "type": "proportional",
                    "configs": {
                        "business": "b3",
                        "percent": 0.8
                    }
                }
            ]
        }

        CompositePolicy(**body)
