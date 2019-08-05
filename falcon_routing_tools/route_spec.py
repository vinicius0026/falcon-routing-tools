from falcon import HTTPError, HTTP_422

def route_spec(params_schema=None, payload_schema=None, description='', summary='', response_schema=None, success_response_code=200):
    """
    Decorator to define a route spec
    params_schema is used to validate query params on the decorated route
    payload_schema is used to validate the payload on the decorated route
    description adds metadata to the route
    """
    def decorator(func):
        def wrapper(self, req, resp, *args, **kwargs):
            validated_params = None
            validated_payload = None

            if params_schema:
                validated_params, errors = params_schema().load(req.params)
                if errors:
                    raise HTTPError(HTTP_422, description=str(errors))

            if payload_schema:
                validated_payload, errors = payload_schema().load(req.media)
                if errors:
                    raise HTTPError(HTTP_422, description=str(errors))

            return func(self, req, resp, *args, validated_params=validated_params, validated_payload=validated_payload, description=description, summary=summary, response_schema=response_schema, success_response_code=success_response_code, **kwargs)
        return wrapper
    return decorator
