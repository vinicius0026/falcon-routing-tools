# falcon routing tools

This package provides helper tools to work with the [falcon](https://github.com/falconry/falcon) framework.

`router.py` provides a decorator to declare route handlers and a way to automatically load all declared decorators.

`route_spec.py` provides a decorator to specify the expected input and the output shape for specific routes, using [Marshmallow](https://github.com/marshmallow-code/marshmallow) schemas.

`api_docs.py` provides a way to generate [Open API](https://github.com/OAI/OpenAPI-Specification) docs from the declared routes.

## Motivation

A minimal falcon app, from their docs, looks like:

```python
# app.py
import falcon

class QuoteResource:
  def on_get(self, req, resp):
    """Handles GET requests"""
    quote = {
      'quote': (
        "I've always been more interested in "
        "the future than in the past."
      ),
      'author': 'Grace Hopper'
    }

    resp.media = quote


api = falcon.API()
api.add_route('/quote', QuoteResource())
```

This is simple and straightforward, but as the application grows, there would be a number of calls to `api.add_route` to register new routes.

Also, as you start breaking up the code into separate files, you'd have to import each of the Resources into the app.py file or into some sort of main router registration file.

The `Router` class provided by falcon-routing-tools helps with both of these issues. So, instead of the minimal code above from falcon, we would have:

```python
# app.py
import falcon
from falcon_routing_tools import Router

app = falcon.API()
router = Router()
base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'routes') # this build the path to ./routes directory
router.load_controllers(base_dir) # and this loads all controllers in that directory, recursively

for route in router.resources:
  app.add_route(route.path, route.resource())
```

```python
# routes/quote.py
from app import router

@router.resource("/quote")
class QuoteResource:
  def on_get(self, req, resp):
    """Handles GET requests"""
    quote = {
      'quote': (
        "I've always been more interested in "
        "the future than in the past."
      ),
      'author': 'Grace Hopper'
    }

    resp.media = quote
```

And any new resources declared under the `routes` path will be automatically registered going forward.

Another issue with the basic falcon example is that the response object is being manually built as a dictionary. In a more realistic case, the data would be read from the database and serialized using some schema. Marshmallow is a widely used serializer and it is used by falcon routing tools validate requests and to generate docs.

With `route_spec` we can register the serializers used in a given route, like so:

```python
# routes/quote.py
from app import router
from falcon_routing_tools import route_spec
from marshmallow import Schema, fields

class QuoteSchema(Schema):
  quote = fields.String()
  author = fields.String()

@router.resource("/quote")
class QuoteResource:

  @route_spec(response_schema=QuoteSchema)
  def on_get(self, req, resp, response_schema, **kwargs):
    # get a quote from the db somehow
    quote = read_quote_from_db()

    # serialize it using the registered serializer
    resp.media = response_schema().dump(quote).data
```

At first glance, we didn't get much benefit from this change, but now we can use the `APIDocs` class to generate Open API documentation automatically for our API.

```python
# app.py
import falcon
from falcon_routing_tools import Router, APIDocs

app = falcon.API()
router = Router()
base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'routes') # this build the path to ./routes directory
router.load_controllers(base_dir) # and this loads all controllers in that directory, recursively

for route in router.resources:
  app.add_route(route.path, route.resource())

docs = APIDocs.generate(router.resources, title="Quotes API") # this will be a dict with the specification of all the routes in the app
```

Maybe more importantly than that, we can use `route_spec` to validate payloads for POST/PUT/PATCH requests and to validate query parameters in any request.

Let's add a POST endpoint to the Quotes resource and use `route_spec` to define how the payload should look like:

```python
# routes/quote.py
from app import router
from falcon_routing_tools import route_spec
from marshmallow import Schema, fields

class QuoteSchema(Schema):
  quote = fields.String()
  author = fields.String()

@router.resource("/quote")
class QuoteResource:

  @route_spec(response_schema=QuoteSchema)
  def on_get(self, req, resp, response_schema, **kwargs):
    # get a quote from the db somehow
    quote = read_quote_from_db()

    # serialize it using the registered serializer
    resp.media = response_schema().dump(quote).data

  @route_spec(payload_schema=QuoteSchema, response_schema=QuoteSchema)
  def on_post(self, req, resp, validated_payload, response_schema, **kwargs):
    # the req.media payload is validated using the registered marshmallow schema and at this point validated_payload is a valid object
    # if validation fails, an HTTPError with code 422 (Unprocessable Entity) is raised
    # we can now safely pass the validated payload to a function that handles creating a new quote
    quote = create_quote(validated_params)

    # and then use the response_schema to serialize the created object
    resp.media = response_schema().dump(quote).data
```

`route_spec` supports the following fields:

Parameter | Type | Purpose
---|---|---
`params_schema` | Marshmallow Schema | Validates the query params of the incoming request
`payload_schema` | Marshmallow Schema | Validates the body of the incoming request
`description` | String | Metadata added to the OpenAPI docs for the route
`summary` | String | Metadata added to the OpenAPI docs for the route
`response_schema` | Marshmallow Schema | Used to generate the response and to create the docs for the route
`error_schema` | Marshmallow Schema | Used to generate error response and to create the docs for the route
`success_response_code` | Number | Allows overriding the response code in the generated APIDocs