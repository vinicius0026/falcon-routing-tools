import sys
import falcon
import pytest
from falcon import testing
from marshmallow import Schema, fields

sys.path.append('../')
sys.path.append('./')

from falcon_routing_tools import route_spec


@pytest.fixture()
def client():

    class BookListParamsSchema(Schema):
        page = fields.Int(missing=1)
        items_per_page = fields.Int(load_from='itemsPerPage', missing=10)
        search_term = fields.String(load_from='searchTerm', missing='')

    class BookCreatePayloadSchema(Schema):
        name = fields.String(required=True)
        author = fields.String(required=True)

    class Books():
        @route_spec(description="list books", params_schema=BookListParamsSchema)
        def on_get(self, req, resp, **kwargs):
            validated_params = kwargs.get('validated_params')
            resp.media = dict(validated_params=validated_params)

        @route_spec(description="create a book", payload_schema=BookCreatePayloadSchema)
        def on_post(self, req, resp, **kwargs):
            validated_payload=kwargs.get('validated_payload')
            resp.media = dict(
                validated_payload=validated_payload
            )

    app = falcon.API()
    app.add_route('/books', Books())

    return testing.TestClient(app)


def test_params_validator_all_defaults(client):
    expected_body = dict(
        validated_params=dict(
            page=1,
            items_per_page=10,
            search_term=''
        )
    )

    response = client.simulate_get('/books')
    assert response.json == expected_body

def test_params_validator_partial_params(client):
    expected_body = dict(
        validated_params=dict(
            page=2,
            items_per_page=5,
            search_term=''
        )
    )

    response = client.simulate_get('/books?page=2&itemsPerPage=5')
    assert response.json == expected_body

def test_params_validator_all_fields_provided(client):
    expected_body = dict(
        validated_params=dict(
            page=3,
            items_per_page=3,
            search_term="search"
        )
    )

    response = client.simulate_get('/books?page=3&itemsPerPage=3&searchTerm=search')
    assert response.json == expected_body

def test_invalid_param(client):
    response = client.simulate_get('/books?page=str')

    assert response.status_code == 422
    assert response.json['description'] == {'page': ['Not a valid integer.']}

def test_payload_validation(client):
    expected_body = dict(
        validated_payload=dict(
            name='name',
            author='author'
        )
    )

    response = client.simulate_post('/books', json=dict(name='name', author='author'))
    assert response.json == expected_body

def test_invalid_payload(client):
    response = client.simulate_post('/books', json=dict(name='name'))

    assert response.status_code == 422
    assert response.json['description'] == {'author': ['Missing data for required field.']}