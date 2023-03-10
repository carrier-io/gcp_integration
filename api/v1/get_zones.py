from flask import request
from flask_restful import Resource
from pydantic import ValidationError

from ...models.integration_pd import IntegrationModel


class API(Resource):

    def __init__(self, module):
        self.module = module

    def post(self):
        try:
            settings = IntegrationModel.parse_obj(request.json)
        except ValidationError as e:
            return e.errors(), 400

        namespaces: list = settings.get_zones()
        return namespaces, 200
