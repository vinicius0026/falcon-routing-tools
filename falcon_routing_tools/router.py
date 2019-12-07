import os
import functools
import re
import pkgutil

class Route():
    def __init__(self, path, resource, prefix):
        self.path = path
        self.resource = resource
        self.prefix = prefix

class Router():
    def __init__(self, prefix=''):
        self.resources = []
        self.prefix = prefix

    def resource(self, path):
        def decorator(Resource):
            route = Route(path, Resource, self.prefix)
            self.resources.append(route)

            @functools.wraps(Resource)
            def wrapper():
                return Resource

            return wrapper
        return decorator

    def load_controllers(self, base_dir, package_name_pattern="^controller$"):
        for path, directories, files in os.walk(base_dir):
            for importer, package_name, _ in pkgutil.iter_modules([path]):
                if re.search(package_name_pattern, package_name):
                    importer.find_module(package_name).load_module(package_name)

