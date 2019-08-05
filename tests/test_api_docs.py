import sys
from marshmallow import Schema, fields

sys.path.append('../')
sys.path.append('./')

from falcon_routing_tools import Router, route_spec, APIDocs


def test_api_docs():
    router = Router()

    class BookSchema(Schema):
        title = fields.String(required=True)
        author = fields.String()
        published_year = fields.Int(load_from='publishedYear')

    class BookResponseSchema(Schema):
        book = fields.Nested(BookSchema)


    @router.resource('/books')
    class Books():
        @route_spec(description='Create Book endpoint', payload_schema=BookSchema, response_schema=BookResponseSchema, success_response_code=201)
        def on_post(self, req, resp, **kwargs):
            resp.media = dict()


    docs = APIDocs.generate(router.resources, title='Books API', version='1.0.0')

    expected_docs = dict(
        openapi='3.0.2',
        info=dict(
            title='Books API',
            version='1.0.0'
        ),
        paths={
            '/books': {
                'post': {
                    'description': 'Create Book endpoint',
                    'requestBody': {
                        'description': 'BookSchema',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'required': ['title'],
                                    'properties': {
                                        'title': {
                                            'type': 'string'
                                        },
                                        'author': {
                                            'type': 'string'
                                        },
                                        'publishedYear': {
                                            'type': 'integer',
                                            'format': 'int32'
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'responses': {
                        "201": {
                            'description': 'success',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'properties': {
                                            'book': {
                                                'properties': {
                                                    'title': {
                                                        'type': 'string'
                                                    },
                                                    'author': {
                                                        'type': 'string'
                                                    },
                                                    'publishedYear': {
                                                        'type': 'integer',
                                                        'format': 'int32'
                                                    }
                                                },
                                                'required': ['title'],
                                                'type': 'object'
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    )

    assert docs == expected_docs