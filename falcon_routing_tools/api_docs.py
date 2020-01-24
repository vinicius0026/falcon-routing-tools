import inspect
from apispec.ext.marshmallow.openapi import OpenAPIConverter
import re

OPEN_API_VERSION = '3.0.2'


class Operation():
    def __init__(self, verb, handler):
        self.verb = verb
        self.handler = handler

class APIDocs():
    @staticmethod
    def generate(routes, title='', version='', options={}):
        return dict(
            openapi=OPEN_API_VERSION,
            info=dict(
                title=title,
                version=version
            ),
            paths={
                APIDocs._clean_path(route.path): APIDocs._get_resource_spec(route)
                for route in routes
            },
            **options,
        )

    @staticmethod
    def _get_resource_spec(route):
        return {
            operation.verb: APIDocs._get_operation_spec(route.resource, operation.handler, route)
            for operation in APIDocs._get_operations_from_resource(route.resource)
        }


    @staticmethod
    def _get_operations_from_resource(resource):
        supported_operations = ['get', 'put', 'post', 'delete', 'patch']

        operations = []

        for operation in supported_operations:
            handler = getattr(resource, f'on_{operation}', None)
            if not handler:
                continue

            operations.append(Operation(operation, handler))

        return operations


    @staticmethod
    def _get_operation_spec(resource, handler, route):
        closure_vars = inspect.getclosurevars(handler)
        description = closure_vars.nonlocals.get('description', '')
        params_schema = closure_vars.nonlocals.get('params_schema')
        payload_schema = closure_vars.nonlocals.get('payload_schema')
        response_schema = closure_vars.nonlocals.get('response_schema')
        success_response_code = closure_vars.nonlocals.get('success_response_code')

        openApiConverter = OpenAPIConverter(OPEN_API_VERSION, lambda s: None, None)

        request_body = {}
        response = {}
        parameters = []

        if getattr(resource, 'tags', False):
            tags = resource.tags
        else:
            tags = APIDocs._get_tags_from_path(route.path)

        if params_schema:
            params_schema_dict = openApiConverter.fields2parameters(params_schema._declared_fields, default_in='query')
            parameters.extend(params_schema_dict)

        route_params = re.findall(r'\{.*\}', route.path)
        for param in route_params:
            parameters.append({
                'name': re.sub(r'\{|\}', '', APIDocs._clean_path(param)),
                'in': 'path',
                'required': True,
            })

        if payload_schema:
            payload_schema_dict = openApiConverter.schema2jsonschema(payload_schema)

            request_body = dict(
                requestBody=dict(
                    description=payload_schema.__name__,
                    content={
                        'application/json': {
                            'schema': payload_schema_dict
                        }
                    }
                )
            )

        if response_schema:
            response_schema_dict = openApiConverter.schema2jsonschema(response_schema)

            response = {
                f'{success_response_code}': {
                    'description': 'success',
                    'content': {
                        'application/json': {
                            'schema': response_schema_dict
                        }
                    }
                }
            }
        else:
            response = {
                f'{success_response_code}': ''
            }


        operation_spec = {
            'description': description,
            'parameters': parameters,
            'responses': {
                **response
            },
            'servers': [ dict(url=route.prefix) ],
            'tags': [ tags ],
            **request_body,
        }

        if getattr(resource, 'no_auth', False):
            operation_spec['security'] = []

        return operation_spec

    @staticmethod
    def _clean_path(path):
        return re.sub(r'\{(.*)(\:.*)\}', r'{\1}', path)

    @staticmethod
    def _get_tags_from_path(path):
        path_tag_blocks = map(
            lambda block: block.capitalize(),
            (
                re.sub(r'^/(v\d/)?', '', path)
                    .split('/')
                    .pop(0)
                    .split('_')
            )
        )

        return ' '.join(path_tag_blocks)
